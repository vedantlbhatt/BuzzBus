using Microsoft.AspNetCore.Mvc;
using BuzzBus.Api.Services;
using BuzzBus.Api.Models;

namespace BuzzBus.Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class RouteSearchController : ControllerBase
    {
        private readonly IRouteService _routeService;

        public RouteSearchController(IRouteService routeService)
        {
            _routeService = routeService;
        }

        [HttpPost]
        public async Task<ActionResult<RouteSearchResponse>> FindRoutes([FromBody] RouteSearchRequest request)
        {
            try
            {
                if (request == null)
                {
                    return BadRequest(new { error = "Request body is required" });
                }

                // Validate that we have at least one valid begin and destination point
                bool hasValidBegin = !string.IsNullOrEmpty(request.BeginBuilding) || 
                                   !string.IsNullOrEmpty(request.BeginCoordinates) || 
                                   !string.IsNullOrEmpty(request.BeginLocation);
                bool hasValidDest = !string.IsNullOrEmpty(request.DestBuilding) || 
                                  !string.IsNullOrEmpty(request.DestCoordinates) || 
                                  !string.IsNullOrEmpty(request.DestLocation);

                if (!hasValidBegin || !hasValidDest)
                {
                    return BadRequest(new { error = "Both begin and destination points must be provided" });
                }

                // Validate building names if provided
                if (!string.IsNullOrEmpty(request.BeginBuilding) || !string.IsNullOrEmpty(request.DestBuilding))
                {
                    var buildings = await _routeService.GetBuildingsAsync();
                    var buildingNames = buildings.Select(b => b.Name).ToHashSet();
                    
                    if (!string.IsNullOrEmpty(request.BeginBuilding) && !buildingNames.Contains(request.BeginBuilding))
                    {
                        return BadRequest(new { error = "Invalid begin building name" });
                    }
                    if (!string.IsNullOrEmpty(request.DestBuilding) && !buildingNames.Contains(request.DestBuilding))
                    {
                        return BadRequest(new { error = "Invalid destination building name" });
                    }
                }

                var result = await _routeService.FindRoutesAsync(request);
                return Ok(result);
            }
            catch (ArgumentException ex)
            {
                return BadRequest(new { error = ex.Message });
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = ex.Message });
            }
        }

        [HttpGet("map-routes")]
        public async Task<ActionResult> GetMapRoutes()
        {
            try
            {
                var routes = await _routeService.GetMapRoutesAsync();
                return Ok(routes);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = ex.Message });
            }
        }

        [HttpGet("map-vehicles")]
        public async Task<ActionResult> GetMapVehicles()
        {
            try
            {
                var vehicles = await _routeService.GetMapVehiclesAsync();
                return Ok(vehicles);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = ex.Message });
            }
        }
    }
}
