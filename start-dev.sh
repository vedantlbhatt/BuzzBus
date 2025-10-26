#!/bin/bash

# Start both React frontend and .NET backend for development

echo "Starting BuzzBus development environment..."

# Function to cleanup background processes on exit
cleanup() {
    echo "Stopping services..."
    kill $REACT_PID $DOTNET_PID 2>/dev/null
    exit
}

# Set up cleanup on script exit
trap cleanup EXIT INT TERM

# Start .NET API in background
echo "Starting .NET API..."
cd BuzzBus.Api
dotnet run &
DOTNET_PID=$!

# Wait a moment for the API to start
sleep 3

# Start React app in background
echo "Starting React app..."
cd ..
npm start &
REACT_PID=$!

echo "Both services are starting..."
echo "React app: http://localhost:3000"
echo ".NET API: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for user to stop
wait
