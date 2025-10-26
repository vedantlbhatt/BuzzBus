using Microsoft.AspNetCore.Mvc;

namespace BuzzBus.Api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class HealthController : ControllerBase
    {
        [HttpGet]
        public ActionResult<object> Get()
        {
            return Ok(new { status = "healthy" });
        }
    }
}
