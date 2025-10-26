namespace BuzzBus.Api.Models
{
    public class RouteSearchResponse
    {
        public List<RouteResult> Routes { get; set; } = new();
        public string BeginBuilding { get; set; } = string.Empty;
        public string DestBuilding { get; set; } = string.Empty;
        public string BeginLocation { get; set; } = string.Empty;
        public string DestLocation { get; set; } = string.Empty;
    }

    public class RouteResult
    {
        public string RouteId { get; set; } = string.Empty;
        public string RouteName { get; set; } = string.Empty;
        public StopInfo BeginStop { get; set; } = new();
        public StopInfo DestStop { get; set; } = new();
        public double TotalWalkingDistance { get; set; }
    }

    public class StopInfo
    {
        public string Name { get; set; } = string.Empty;
        public double Distance { get; set; }
    }
}
