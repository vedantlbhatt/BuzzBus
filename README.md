# BuzzBus - Georgia Tech Bus Route Finder

A modern web application that helps Georgia Tech students and visitors find the best bus routes between campus buildings and nearby locations.

## Architecture

- **Frontend**: React 18 with modern CSS
- **Backend**: .NET 8 Web API
- **External API**: TransLoc API for real-time bus data

## Prerequisites

- Node.js 16+ and npm
- .NET 8 SDK ([Download here](https://dotnet.microsoft.com/download/dotnet/8.0))
- TransLoc API key and base URL

### Alternative: Docker Setup

If you prefer not to install .NET locally, you can use Docker:

- Docker Desktop
- Docker Compose

## Docker Setup (Alternative)

1. Copy the environment file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` with your TransLoc API credentials

3. Run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

This will start both the .NET API and React frontend in containers.

## Setup Instructions

### 1. Backend (.NET API)

1. Navigate to the API directory:
   ```bash
   cd BuzzBus.Api
   ```

2. Install dependencies:
   ```bash
   dotnet restore
   ```

3. Configure the API settings in `appsettings.json`:
   ```json
   {
     "TranslocApi": {
       "ApiKey": "YOUR_TRANSLOC_API_KEY",
       "BaseUrl": "YOUR_GT_TRANSLOC_BASE_URL"
     }
   }
   ```

4. Run the API:
   ```bash
   dotnet run
   ```

The API will be available at `http://localhost:5000`

### 2. Frontend (React)

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

The React app will be available at `http://localhost:3000`

## API Endpoints

- `GET /api/buildings` - Get list of available campus buildings
- `POST /api/route-search` - Find bus routes between two locations
- `GET /api/health` - Health check endpoint

## Features

- **Building-to-Building Search**: Select from predefined Georgia Tech buildings
- **Location-to-Location Search**: Use Google Places API for custom locations
- **Real-time Data**: Shows only routes with currently active buses
- **Walking Distance**: Calculates total walking distance to/from bus stops
- **Responsive Design**: Works on desktop and mobile devices

## Project Structure

```
BuzzBus/
├── BuzzBus.Api/                 # .NET Web API backend
│   ├── Controllers/             # API controllers
│   ├── Models/                  # Data models
│   ├── Services/                # Business logic services
│   └── Program.cs              # Application entry point
├── src/                        # React frontend
│   ├── App.js                  # Main React component
│   ├── App.css                 # Styling
│   └── index.js                # React entry point
├── public/                     # Static assets
└── package.json                # Node.js dependencies
```

## Development

### Running Both Services

1. Start the .NET API (Terminal 1):
   ```bash
   cd BuzzBus.Api
   dotnet run
   ```

2. Start the React app (Terminal 2):
   ```bash
   npm start
   ```

### Building for Production

1. Build the React app:
   ```bash
   npm run build
   ```

2. Build the .NET API:
   ```bash
   cd BuzzBus.Api
   dotnet publish -c Release
   ```

## Configuration

The application requires the following environment variables or configuration:

- `TranslocApi:ApiKey` - Your TransLoc API key
- `TranslocApi:BaseUrl` - Georgia Tech TransLoc API base URL

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.