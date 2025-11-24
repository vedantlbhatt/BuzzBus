#!/bin/bash

# Start both React frontend and FastAPI backend for development

echo "Starting BuzzBus development environment..."

# Function to cleanup background processes on exit
cleanup() {
    echo "Stopping services..."
    kill $REACT_PID $FASTAPI_PID 2>/dev/null
    exit
}

# Set up cleanup on script exit
trap cleanup EXIT INT TERM

# Start FastAPI backend in background
echo "Starting FastAPI backend..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 5000 --reload &
FASTAPI_PID=$!

# Wait a moment for the API to start
sleep 3

# Start React app in background
echo "Starting React app..."
cd ..
npm start &
REACT_PID=$!

echo "Both services are starting..."
echo "React app: http://localhost:3000"
echo "FastAPI backend: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both services"

# Wait for user to stop
wait
