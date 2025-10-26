namespace BuzzBus.Api.Models
{
    public class MapRoute
    {
        public string RouteId { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string MapLineColor { get; set; } = string.Empty;
        public double MapLatitude { get; set; }
        public double MapLongitude { get; set; }
        public int MapZoom { get; set; }
        public bool IsVisibleOnMap { get; set; }
        public bool IsCheckedOnMap { get; set; }
        public bool HideRouteLine { get; set; }
        public string EncodedPolyline { get; set; } = string.Empty;
        public List<MapStop> Stops { get; set; } = new List<MapStop>();
    }

    public class MapStop
    {
        public string RouteStopId { get; set; } = string.Empty;
        public string RouteId { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public double Latitude { get; set; }
        public double Longitude { get; set; }
        public int Order { get; set; }
        public bool ShowEstimatesOnMap { get; set; }
        public bool ShowDefaultedOnMap { get; set; }
    }
}
