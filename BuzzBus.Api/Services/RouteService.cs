using BuzzBus.Api.Models;
using System.Text.Json;

namespace BuzzBus.Api.Services
{
    public class RouteService : IRouteService
    {
        private readonly ITranslocApiService _translocApiService;
        private readonly Dictionary<string, Building> _buildings;

        public RouteService(ITranslocApiService translocApiService)
        {
            _translocApiService = translocApiService;
            _buildings = new Dictionary<string, Building>
            {
                ["Tech Tower"] = new Building { Name = "Tech Tower", Latitude = 33.7726510852488, Longitude = -84.3947508475869 },
                ["Georgia Tech Library"] = new Building { Name = "Georgia Tech Library", Latitude = 33.7747751124862, Longitude = -84.39575939176652 },
                ["Clough Commons"] = new Building { Name = "Clough Commons", Latitude = 33.77532604620433, Longitude = -84.39637188806334 },
                ["Hopkins Hall"] = new Building { Name = "Hopkins Hall", Latitude = 33.77850642030214, Longitude = -84.39069072993782 },
                ["Glenn Hall"] = new Building { Name = "Glenn Hall", Latitude = 33.77397354313724, Longitude = -84.39167014943847 },
                ["North Ave East"] = new Building { Name = "North Ave East", Latitude = 33.769581436909526, Longitude = -84.39098961634303 },
                ["Student Center"] = new Building { Name = "Student Center", Latitude = 33.77361305511324, Longitude = -84.39801594997785 },
                ["Campus Rec Center"] = new Building { Name = "Campus Rec Center", Latitude = 33.77559002203094, Longitude = -84.40334559002532 },
                ["D.M. Smith"] = new Building { Name = "D.M. Smith", Latitude = 33.77158232011701, Longitude = -84.3911280052064 },
                ["Bobby Dodd Stadium"] = new Building { Name = "Bobby Dodd Stadium", Latitude = 33.772681846343005, Longitude = -84.39323608111707 }
            };
        }

        public Task<List<Building>> GetBuildingsAsync()
        {
            return Task.FromResult(_buildings.Values.ToList());
        }

        public async Task<RouteSearchResponse> FindRoutesAsync(RouteSearchRequest request)
        {
            (double beginLat, double beginLng, string beginName) = GetBeginPoint(request);
            (double destLat, double destLng, string destName) = GetDestPoint(request);

            var allStops = new List<(double lat, double lng, string desc, string routeId)>();

            // Get all routes and filter to only active ones
            var activeRoutes = await _translocApiService.GetActiveRoutesAsync();

            if (!activeRoutes.Any())
            {
                return new RouteSearchResponse
                {
                    Routes = new List<RouteResult>(),
                    BeginBuilding = beginName,
                    DestBuilding = destName,
                    BeginLocation = beginName,
                    DestLocation = destName
                };
            }

            foreach (var route in activeRoutes)
            {
                var routeElement = JsonSerializer.Deserialize<JsonElement>(JsonSerializer.Serialize(route));
                if (routeElement.TryGetProperty("RouteID", out var routeIdElement))
                {
                    string routeId;
                    if (routeIdElement.ValueKind == JsonValueKind.Number)
                    {
                        routeId = routeIdElement.GetInt32().ToString();
                    }
                    else
                    {
                        routeId = routeIdElement.GetString() ?? "";
                    }
                    
                    if (!string.IsNullOrEmpty(routeId))
                    {
                        var stops = await _translocApiService.GetStopsAsync(routeId);
                        foreach (var stop in stops)
                        {
                            var stopElement = JsonSerializer.Deserialize<JsonElement>(JsonSerializer.Serialize(stop));
                            if (stopElement.TryGetProperty("Latitude", out var latElement) &&
                                stopElement.TryGetProperty("Longitude", out var lngElement) &&
                                stopElement.TryGetProperty("Description", out var descElement))
                            {
                                var lat = latElement.GetDouble();
                                var lng = lngElement.GetDouble();
                                var desc = descElement.GetString() ?? "";
                                allStops.Add((lat, lng, desc, routeId));
                            }
                        }
                    }
                }
            }

            // Group stops by route
            var stopsByRoute = allStops.GroupBy(s => s.routeId).ToDictionary(g => g.Key, g => g.ToList());

            var routeCosts = new List<(double cost, string routeId, (double lat, double lng, string desc, string routeId) beginStop, (double lat, double lng, string desc, string routeId) destStop)>();

            foreach (var routeGroup in stopsByRoute)
            {
                var routeId = routeGroup.Key;
                var routeStops = routeGroup.Value;
                if (!routeStops.Any()) continue;

                // Find the best start stop (closest to begin point)
                var bestStartStop = routeStops.MinBy(s => HaversineDistance(s.lat, s.lng, beginLat, beginLng));
                var startWalkingDistance = HaversineDistance(bestStartStop.lat, bestStartStop.lng, beginLat, beginLng);

                // Only consider routes where we don't have to walk too far to get to the bus
                const double maxStartWalkingDistance = 1000; // 1km max walking to bus
                if (startWalkingDistance > maxStartWalkingDistance) continue;

                // Find the best destination stop (closest to destination point)
                var bestDestStop = routeStops.MinBy(s => HaversineDistance(s.lat, s.lng, destLat, destLng));
                var destWalkingDistance = HaversineDistance(bestDestStop.lat, bestDestStop.lng, destLat, destLng);

                // Only consider routes where we don't have to walk too far from the bus
                const double maxDestWalkingDistance = 1000; // 1km max walking from bus
                if (destWalkingDistance > maxDestWalkingDistance) continue;

                // Calculate total walking distance
                var totalWalkingDistance = startWalkingDistance + destWalkingDistance;

                // Add penalty if start and dest stops are the same (not useful)
                if (bestStartStop.desc == bestDestStop.desc)
                {
                    totalWalkingDistance += 1000; // Heavy penalty for same stop
                }

                routeCosts.Add((totalWalkingDistance, routeId, bestStartStop, bestDestStop));
            }

            routeCosts.Sort((a, b) => a.cost.CompareTo(b.cost));

            var maxDisplay = 5;
            var topRoutes = routeCosts.Take(maxDisplay);

            var results = new List<RouteResult>();
            foreach (var (totalCost, routeId, beginStop, destStop) in topRoutes)
            {
                var routeDetails = await _translocApiService.GetRouteDetailsAsync(routeId);
                if (!routeDetails.Any()) continue;

                var routeElement = JsonSerializer.Deserialize<JsonElement>(JsonSerializer.Serialize(routeDetails[0]));
                var routeName = routeElement.TryGetProperty("Description", out var descElement) ? descElement.GetString() ?? "N/A" : "N/A";

                var distBegin = HaversineDistance(beginStop.lat, beginStop.lng, beginLat, beginLng);
                var distDest = HaversineDistance(destStop.lat, destStop.lng, destLat, destLng);

                results.Add(new RouteResult
                {
                    RouteId = routeId,
                    RouteName = routeName,
                    BeginStop = new StopInfo
                    {
                        Name = beginStop.desc,
                        Distance = Math.Round(distBegin, 1)
                    },
                    DestStop = new StopInfo
                    {
                        Name = destStop.desc,
                        Distance = Math.Round(distDest, 1)
                    },
                    TotalWalkingDistance = Math.Round(totalCost, 1)
                });
            }

            return new RouteSearchResponse
            {
                Routes = results,
                BeginBuilding = beginName,
                DestBuilding = destName,
                BeginLocation = beginName,
                DestLocation = destName
            };
        }

        private (double lat, double lng, string name) GetBeginPoint(RouteSearchRequest request)
        {
            // Try building first
            if (!string.IsNullOrEmpty(request.BeginBuilding) && _buildings.ContainsKey(request.BeginBuilding))
            {
                var building = _buildings[request.BeginBuilding];
                return (building.Latitude, building.Longitude, building.Name);
            }
            
            // Try coordinates
            if (!string.IsNullOrEmpty(request.BeginCoordinates))
            {
                var coords = request.BeginCoordinates.Split(',');
                if (coords.Length == 2 && double.TryParse(coords[0], out var lat) && double.TryParse(coords[1], out var lng))
                {
                    return (lat, lng, request.BeginLocation ?? "Starting Location");
                }
            }
            
            // Try location name (fallback to Georgia Tech coordinates)
            if (!string.IsNullOrEmpty(request.BeginLocation))
            {
                return (33.7756, -84.3963, request.BeginLocation);
            }
            
            throw new ArgumentException("Invalid begin point");
        }

        private (double lat, double lng, string name) GetDestPoint(RouteSearchRequest request)
        {
            // Try building first
            if (!string.IsNullOrEmpty(request.DestBuilding) && _buildings.ContainsKey(request.DestBuilding))
            {
                var building = _buildings[request.DestBuilding];
                return (building.Latitude, building.Longitude, building.Name);
            }
            
            // Try coordinates
            if (!string.IsNullOrEmpty(request.DestCoordinates))
            {
                var coords = request.DestCoordinates.Split(',');
                if (coords.Length == 2 && double.TryParse(coords[0], out var lat) && double.TryParse(coords[1], out var lng))
                {
                    return (lat, lng, request.DestLocation ?? "Destination Location");
                }
            }
            
            // Try location name (fallback to Georgia Tech coordinates)
            if (!string.IsNullOrEmpty(request.DestLocation))
            {
                return (33.7756, -84.3963, request.DestLocation);
            }
            
            throw new ArgumentException("Invalid destination point");
        }

        private static double HaversineDistance(double lat1, double lon1, double lat2, double lon2)
        {
            const double R = 6371000; // meters
            var dlat = ToRadians(lat2 - lat1);
            var dlon = ToRadians(lon2 - lon1);
            var a = Math.Sin(dlat / 2) * Math.Sin(dlat / 2) +
                    Math.Cos(ToRadians(lat1)) * Math.Cos(ToRadians(lat2)) *
                    Math.Sin(dlon / 2) * Math.Sin(dlon / 2);
            var c = 2 * Math.Atan2(Math.Sqrt(a), Math.Sqrt(1 - a));
            return R * c;
        }

        private static double ToRadians(double degrees)
        {
            return degrees * Math.PI / 180;
        }
    }
}
