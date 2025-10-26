using Microsoft.AspNetCore.Mvc;
using BuzzBus.Api.Services;
using BuzzBus.Api.Models;

namespace BuzzBus.Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class BuildingsController : ControllerBase
    {
        private readonly IRouteService _routeService;

        public BuildingsController(IRouteService routeService)
        {
            _routeService = routeService;
        }

        [HttpGet]
        public async Task<ActionResult<List<string>>> GetBuildings()
        {
            try
            {
                // Temporarily return hardcoded buildings for testing
                var hardcodedBuildings = new List<string>
                {
                    "Tech Tower",
                    "Georgia Tech Library", 
                    "Clough Commons",
                    "Hopkins Hall",
                    "Glenn Hall",
                    "North Ave East",
                    "Student Center",
                    "Campus Rec Center",
                    "D.M. Smith",
                    "Bobby Dodd Stadium"
                };
                
                return Ok(hardcodedBuildings);
                
                // TODO: Uncomment when Transloc API is working
                // var buildings = await _routeService.GetBuildingsAsync();
                // return Ok(buildings.Select(b => b.Name).ToList());
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = ex.Message });
            }
        }
    }
}
