namespace BuzzBus.Api.Models
{
    public class MapVehicle
    {
        public string VehicleId { get; set; } = string.Empty;
        public string RouteId { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public double Latitude { get; set; }
        public double Longitude { get; set; }
        public double GroundSpeed { get; set; }
        public double Heading { get; set; }
        public int Seconds { get; set; }
        public bool IsOnRoute { get; set; }
        public bool IsDelayed { get; set; }
    }
}
