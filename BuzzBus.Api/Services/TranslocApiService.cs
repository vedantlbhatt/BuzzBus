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
            var endpoint = "/GetRoutes";
            var url = $"{_settings.BaseUrl}{endpoint}?APIKey={_settings.ApiKey}";
            
            try
            {
                var response = await _httpClient.GetAsync(url);
                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    return JsonSerializer.Deserialize<List<object>>(content) ?? new List<object>();
                }
                else
                {
                    Console.WriteLine($"TransLoc API error: {response.StatusCode} - {response.ReasonPhrase}");
                    return new List<object>();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"TransLoc API exception: {ex.Message}");
                return new List<object>();
            }
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
                    string routeId;
                    if (routeIdElement.ValueKind == JsonValueKind.Number)
                    {
                        routeId = routeIdElement.GetInt32().ToString();
                    }
                    else
                    {
                        routeId = routeIdElement.GetString() ?? "";
                    }
                    return !string.IsNullOrEmpty(routeId) && activeRouteIds.Contains(routeId);
                }
                return false;
            }).ToList();
        }

        public async Task<List<object>> GetStopsAsync(string routeId)
        {
            var endpoint = "/GetStops";
            var url = $"{_settings.BaseUrl}{endpoint}?APIKey={_settings.ApiKey}&routeID={routeId}";
            
            try
            {
                var response = await _httpClient.GetAsync(url);
                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    return JsonSerializer.Deserialize<List<object>>(content) ?? new List<object>();
                }
                else
                {
                    Console.WriteLine($"TransLoc API error for stops: {response.StatusCode} - {response.ReasonPhrase}");
                    return new List<object>();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"TransLoc API exception for stops: {ex.Message}");
                return new List<object>();
            }
        }

        public async Task<List<object>> GetRouteDetailsAsync(string routeId)
        {
            var endpoint = "/GetRoutes";
            var url = $"{_settings.BaseUrl}{endpoint}?APIKey={_settings.ApiKey}&routeID={routeId}";
            
            try
            {
                var response = await _httpClient.GetAsync(url);
                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    return JsonSerializer.Deserialize<List<object>>(content) ?? new List<object>();
                }
                else
                {
                    Console.WriteLine($"TransLoc API error for route details: {response.StatusCode} - {response.ReasonPhrase}");
                    return new List<object>();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"TransLoc API exception for route details: {ex.Message}");
                return new List<object>();
            }
        }

        public async Task<Dictionary<string, List<object>>> GetActiveVehiclesAsync()
        {
            var endpoint = "/GetMapVehiclePoints";
            var url = $"{_settings.BaseUrl}{endpoint}?APIKey={_settings.ApiKey}";
            
            try
            {
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
                            string routeId;
                            if (routeIdElement.ValueKind == JsonValueKind.Number)
                            {
                                routeId = routeIdElement.GetInt32().ToString();
                            }
                            else
                            {
                                routeId = routeIdElement.GetString();
                            }
                            
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
                else
                {
                    Console.WriteLine($"TransLoc API error: {response.StatusCode} - {response.ReasonPhrase}");
                    return new Dictionary<string, List<object>>();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"TransLoc API exception: {ex.Message}");
                return new Dictionary<string, List<object>>();
            }
        }

        public async Task<List<object>> GetRoutesForMapWithScheduleWithEncodedLineAsync()
        {
            var endpoint = "/GetRoutesForMapWithScheduleWithEncodedLine";
            var url = $"{_settings.BaseUrl}{endpoint}?APIKey={_settings.ApiKey}";
            
            try
            {
                var response = await _httpClient.GetAsync(url);
                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    return JsonSerializer.Deserialize<List<object>>(content) ?? new List<object>();
                }
                else
                {
                    Console.WriteLine($"TransLoc API error for map routes: {response.StatusCode} - {response.ReasonPhrase}");
                    return new List<object>();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"TransLoc API exception for map routes: {ex.Message}");
                return new List<object>();
            }
        }

        public async Task<List<object>> GetMapVehiclePointsAsync()
        {
            var endpoint = "/GetMapVehiclePoints";
            var url = $"{_settings.BaseUrl}{endpoint}?APIKey={_settings.ApiKey}";
            
            try
            {
                var response = await _httpClient.GetAsync(url);
                if (response.IsSuccessStatusCode)
                {
                    var content = await response.Content.ReadAsStringAsync();
                    return JsonSerializer.Deserialize<List<object>>(content) ?? new List<object>();
                }
                else
                {
                    Console.WriteLine($"TransLoc API error for vehicle points: {response.StatusCode} - {response.ReasonPhrase}");
                    return new List<object>();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"TransLoc API exception for vehicle points: {ex.Message}");
                return new List<object>();
            }
        }
    }
}
