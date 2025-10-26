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
                var buildings = await _routeService.GetBuildingsAsync();
                return Ok(buildings.Select(b => b.Name).ToList());
            }
            catch (Exception ex)
            {
                return StatusCode(500, new { error = ex.Message });
            }
        }
    }
}
