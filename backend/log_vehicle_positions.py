#!/usr/bin/env python3
"""
Collect per-minute vehicle telemetry from the TransLoc API and store it locally.

Usage:
    python log_vehicle_positions.py --duration-minutes 480 --interval-seconds 60
"""

import argparse
import asyncio
import csv
import json
import logging
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

# Ensure we can import project modules when running as a script
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.transloc_api_service import TranslocApiService  # noqa: E402

LOGGER = logging.getLogger("vehicle_logger")

FIELDNAMES = [
    "timestamp",
    "route_id",
    "vehicle_id",
    "vehicle_name",
    "latitude",
    "longitude",
    "ground_speed",
    "heading",
    "seconds_since_report",
    "is_on_route",
    "is_delayed",
]


def _default_output_dir() -> Path:
    return SCRIPT_DIR / "data" / "vehicle_positions"


def write_rows(csv_path: Path, rows: List[Dict[str, object]]) -> None:
    """Append rows to CSV, writing a header if the file is new."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = csv_path.exists()

    with csv_path.open("a", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


async def snapshot_route_metadata(service: TranslocApiService, session_dir: Path) -> Path:
    """Fetch current route + stop metadata once per session for reference."""
    metadata_path = session_dir / "route_metadata.json"
    LOGGER.info("Capturing route + stop metadata …")

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "routes": [],
        "stops_by_route": {},
    }

    routes = await service.get_routes_for_map_with_schedule_with_encoded_line()
    metadata["routes"] = routes

    stops_by_route: Dict[str, List[dict]] = {}
    for route in routes:
        route_id = service._extract_route_id(route)
        if not route_id:
            continue
        stops = await service.get_stops(route_id)
        stops_by_route[route_id] = stops

    metadata["stops_by_route"] = stops_by_route
    metadata_path.write_text(json.dumps(metadata, indent=2))

    LOGGER.info("Route metadata stored at %s", metadata_path)
    return metadata_path


async def collect_positions(
    duration_minutes: int,
    interval_seconds: int,
    output_dir: Path,
    max_iterations: int | None = None,
) -> Path:
    """Run the polling loop and persist position data."""
    service = TranslocApiService()
    session_start = datetime.now(timezone.utc)
    session_dir = output_dir / session_start.strftime("%Y%m%d-%H%M%S")
    session_dir.mkdir(parents=True, exist_ok=True)

    session_info = {
        "session_start": session_start.isoformat(),
        "interval_seconds": interval_seconds,
        "duration_minutes": duration_minutes,
        "output_dir": str(session_dir),
    }
    (session_dir / "session.json").write_text(json.dumps(session_info, indent=2))

    csv_path = session_dir / "vehicle_positions.csv"

    # Capture static metadata up-front to support later visualization.
    await snapshot_route_metadata(service, session_dir)

    iteration = 0
    rows_written = 0
    end_time = (
        session_start + timedelta(minutes=duration_minutes)
        if duration_minutes > 0
        else None
    )

    LOGGER.info(
        "Starting telemetry capture: interval=%ss duration=%s mins output=%s",
        interval_seconds,
        "∞" if end_time is None else duration_minutes,
        csv_path,
    )

    try:
        while True:
            now = datetime.now(timezone.utc)
            if end_time and now >= end_time:
                LOGGER.info("Reached configured duration; stopping collection.")
                break
            if max_iterations and iteration >= max_iterations:
                LOGGER.info("Reached max iterations (%s); stopping collection.", max_iterations)
                break

            iteration += 1
            loop_start = time.monotonic()

            try:
                vehicles = await service.get_map_vehicle_points()
            except Exception as exc:  # pragma: no cover - defensive logging
                LOGGER.error("Failed to fetch vehicle points: %s", exc, exc_info=True)
                vehicles = []

            timestamp = datetime.now(timezone.utc).isoformat()
            rows: List[Dict[str, object]] = []
            for vehicle in vehicles:
                row = {
                    "timestamp": timestamp,
                    "route_id": service._extract_route_id(vehicle),
                    "vehicle_id": vehicle.get("VehicleID"),
                    "vehicle_name": vehicle.get("Name"),
                    "latitude": vehicle.get("Latitude"),
                    "longitude": vehicle.get("Longitude"),
                    "ground_speed": vehicle.get("GroundSpeed"),
                    "heading": vehicle.get("Heading"),
                    "seconds_since_report": vehicle.get("Seconds"),
                    "is_on_route": vehicle.get("IsOnRoute"),
                    "is_delayed": vehicle.get("IsDelayed"),
                }
                rows.append(row)

            if rows:
                write_rows(csv_path, rows)
                rows_written += len(rows)
                LOGGER.info(
                    "[%s] Logged %s vehicles (total rows=%s)",
                    timestamp,
                    len(rows),
                    rows_written,
                )
            else:
                LOGGER.warning("[%s] No vehicles reported.", timestamp)

            elapsed = time.monotonic() - loop_start
            sleep_for = max(0, interval_seconds - elapsed)
            await asyncio.sleep(sleep_for)
    finally:
        await service.close()

    LOGGER.info("Collection complete. Data stored at %s", csv_path)
    return session_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Log per-minute vehicle positions from TransLoc."
    )
    parser.add_argument(
        "--duration-minutes",
        type=int,
        default=480,
        help="How long to collect data (default: 480 minutes = 8 hours).",
    )
    parser.add_argument(
        "--interval-seconds",
        type=int,
        default=60,
        help="Sampling interval in seconds (default: 60).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=_default_output_dir(),
        help="Directory where session folders will be written.",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Optional cap on iterations (useful for testing).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )
    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    await collect_positions(
        duration_minutes=args.duration_minutes,
        interval_seconds=args.interval_seconds,
        output_dir=args.output_dir,
        max_iterations=args.max_iterations,
    )


if __name__ == "__main__":
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nTelemetry collection interrupted by user.")



