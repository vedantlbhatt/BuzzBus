using BuzzBus.Api.Models;

namespace BuzzBus.Api.Services
{
    public interface ITranslocApiService
    {
        Task<List<object>> GetAllRoutesAsync();
        Task<List<object>> GetActiveRoutesAsync();
        Task<List<object>> GetStopsAsync(string routeId);
        Task<List<object>> GetRouteDetailsAsync(string routeId);
        Task<Dictionary<string, List<object>>> GetActiveVehiclesAsync();
        Task<List<object>> GetRoutesForMapWithScheduleWithEncodedLineAsync();
        Task<List<object>> GetMapVehiclePointsAsync();
    }
}
