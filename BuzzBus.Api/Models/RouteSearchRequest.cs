using System.Text.Json.Serialization;

namespace BuzzBus.Api.Models
{
    public class RouteSearchRequest
    {
        // Building-based search
        [JsonPropertyName("begin_building")]
        public string? BeginBuilding { get; set; }
        
        [JsonPropertyName("dest_building")]
        public string? DestBuilding { get; set; }
        
        // Location-based search
        [JsonPropertyName("begin_location")]
        public string? BeginLocation { get; set; }
        
        [JsonPropertyName("dest_location")]
        public string? DestLocation { get; set; }
        
        [JsonPropertyName("begin_coordinates")]
        public string? BeginCoordinates { get; set; }
        
        [JsonPropertyName("dest_coordinates")]
        public string? DestCoordinates { get; set; }
    }
}
