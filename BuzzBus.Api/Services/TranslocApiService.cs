using BuzzBus.Api.Models;
using Microsoft.Extensions.Options;
using System.Text.Json;

namespace BuzzBus.Api.Services
{
    public class TranslocApiService : ITranslocApiService
    {
        private readonly HttpClient _httpClient;
        private readonly TranslocApiSettings _settings;

        public TranslocApiService(HttpClient httpClient, IOptions<TranslocApiSettings> settings)
        {
            _httpClient = httpClient;
            _settings = settings.Value;
        }

        public async Task<List<object>> GetAllRoutesAsync()
        {
            // Mock data for testing - replace with real API call when credentials are working
            return new List<object>
            {
                new { RouteID = "4001480", Description = "Tech Trolley", LongName = "Tech Trolley" },
                new { RouteID = "4001481", Description = "Red Route", LongName = "Red Route" },
                new { RouteID = "4001482", Description = "Blue Route", LongName = "Blue Route" }
            };
            
            /* Real API call - uncomment when credentials are working
            var endpoint = "/GetRoutesForMapWithScheduleWithEncodedLine";
            var url = $"{_settings.BaseUrl}{endpoint}?APIKey={_settings.ApiKey}";
            
            var response = await _httpClient.GetAsync(url);
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync();
                return JsonSerializer.Deserialize<List<object>>(content) ?? new List<object>();
            }
            return new List<object>();
            */
        }

        public async Task<List<object>> GetActiveRoutesAsync()
        {
            var allRoutes = await GetAllRoutesAsync();
            var activeVehicles = await GetActiveVehiclesAsync();
            
            var activeRouteIds = activeVehicles.Keys.ToHashSet();
            
            return allRoutes.Where(route =>
            {
                var routeElement = JsonSerializer.Deserialize<JsonElement>(JsonSerializer.Serialize(route));
                if (routeElement.TryGetProperty("RouteID", out var routeIdElement))
                {
                    var routeId = routeIdElement.GetString();
                    return !string.IsNullOrEmpty(routeId) && activeRouteIds.Contains(routeId);
                }
                return false;
            }).ToList();
        }

        public async Task<List<object>> GetStopsAsync(string routeId)
        {
            // Mock data for testing - simulate stops for routes
            return new List<object>
            {
                new { 
                    Latitude = 33.7726510852488, 
                    Longitude = -84.3947508475869, 
                    Description = "Tech Tower Stop",
                    StopID = "1"
                },
                new { 
                    Latitude = 33.77361305511324, 
                    Longitude = -84.39801594997785, 
                    Description = "Student Center Stop",
                    StopID = "2"
                },
                new { 
                    Latitude = 33.77532604620433, 
                    Longitude = -84.39637188806334, 
                    Description = "Clough Commons Stop",
                    StopID = "3"
                }
            };
            
            /* Real API call - uncomment when credentials are working
            var endpoint = "/GetStops";
            var url = $"{_settings.BaseUrl}{endpoint}?APIKey={_settings.ApiKey}&routeID={routeId}";
            
            var response = await _httpClient.GetAsync(url);
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync();
                return JsonSerializer.Deserialize<List<object>>(content) ?? new List<object>();
            }
            return new List<object>();
            */
        }

        public async Task<List<object>> GetRouteDetailsAsync(string routeId)
        {
            // Mock data for testing - simulate route details
            return new List<object>
            {
                new { 
                    RouteID = routeId, 
                    Description = routeId == "4001480" ? "Tech Trolley" : 
                                 routeId == "4001481" ? "Red Route" : "Blue Route",
                    LongName = routeId == "4001480" ? "Tech Trolley" : 
                              routeId == "4001481" ? "Red Route" : "Blue Route"
                }
            };
            
            /* Real API call - uncomment when credentials are working
            var endpoint = "/GetRoutes";
            var url = $"{_settings.BaseUrl}{endpoint}?APIKey={_settings.ApiKey}&routeID={routeId}";
            
            var response = await _httpClient.GetAsync(url);
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync();
                return JsonSerializer.Deserialize<List<object>>(content) ?? new List<object>();
            }
            return new List<object>();
            */
        }

        public async Task<Dictionary<string, List<object>>> GetActiveVehiclesAsync()
        {
            // Mock data for testing - simulate active vehicles
            return new Dictionary<string, List<object>>
            {
                ["4001480"] = new List<object> { new { RouteID = "4001480", VehicleID = "123" } },
                ["4001481"] = new List<object> { new { RouteID = "4001481", VehicleID = "124" } }
            };
            
            /* Real API call - uncomment when credentials are working
            var endpoint = "/GetMapVehiclePoints";
            var url = $"{_settings.BaseUrl}{endpoint}?APIKey={_settings.ApiKey}";
            
            var response = await _httpClient.GetAsync(url);
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadAsStringAsync();
                var vehicles = JsonSerializer.Deserialize<List<object>>(content) ?? new List<object>();
                
                var routeVehicles = new Dictionary<string, List<object>>();
                foreach (var vehicle in vehicles)
                {
                    var vehicleElement = JsonSerializer.Deserialize<JsonElement>(JsonSerializer.Serialize(vehicle));
                    if (vehicleElement.TryGetProperty("RouteID", out var routeIdElement))
                    {
                        var routeId = routeIdElement.GetString();
                        if (!string.IsNullOrEmpty(routeId))
                        {
                            if (!routeVehicles.ContainsKey(routeId))
                                routeVehicles[routeId] = new List<object>();
                            routeVehicles[routeId].Add(vehicle);
                        }
                    }
                }
                return routeVehicles;
            }
            return new Dictionary<string, List<object>>();
            */
        }
    }
}
