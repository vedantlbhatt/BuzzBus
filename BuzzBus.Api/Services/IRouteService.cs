using BuzzBus.Api.Models;

namespace BuzzBus.Api.Services
{
    public interface IRouteService
    {
        Task<List<Building>> GetBuildingsAsync();
        Task<RouteSearchResponse> FindRoutesAsync(RouteSearchRequest request);
        Task<List<MapRoute>> GetMapRoutesAsync();
        Task<List<MapVehicle>> GetMapVehiclesAsync();
    }
}
