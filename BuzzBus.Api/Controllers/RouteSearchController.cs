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

                // Validate building-based search
                if (!string.IsNullOrEmpty(request.BeginBuilding) && !string.IsNullOrEmpty(request.DestBuilding))
                {
                    var buildings = await _routeService.GetBuildingsAsync();
                    var buildingNames = buildings.Select(b => b.Name).ToHashSet();
                    
                    if (!buildingNames.Contains(request.BeginBuilding))
                    {
                        return BadRequest(new { error = "Invalid begin building name" });
                    }
                    if (!buildingNames.Contains(request.DestBuilding))
                    {
                        return BadRequest(new { error = "Invalid destination building name" });
                    }
                }
                // Validate location-based search
                else if (!string.IsNullOrEmpty(request.BeginCoordinates) && !string.IsNullOrEmpty(request.DestCoordinates))
                {
                    if (string.IsNullOrEmpty(request.BeginLocation) || string.IsNullOrEmpty(request.DestLocation))
                    {
                        return BadRequest(new { error = "Location names are required for coordinate-based search" });
                    }
                }
                else
                {
                    return BadRequest(new { error = "Either building names or coordinates must be provided" });
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
    }
}
