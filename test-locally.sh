#!/bin/bash

echo "=== Testing BuzzBus Locally ==="
echo ""

# Check if backend is running
echo "1. Checking backend..."
if curl -s http://localhost:5001/api/buildings > /dev/null 2>&1; then
    echo "   ✓ Backend is running on port 5001"
else
    echo "   ✗ Backend is NOT running"
    echo "   Start it with: cd BuzzBus.Api && dotnet run --urls 'http://localhost:5001'"
    exit 1
fi

# Build the production version
echo ""
echo "2. Building production version..."
npm run build

if [ $? -ne 0 ]; then
    echo "   ✗ Build failed!"
    exit 1
fi

echo "   ✓ Build successful"

# Check what URLs are in the build
echo ""
echo "3. Checking built code for API URLs..."
if grep -q "buzzbus-production" build/static/js/main.*.js 2>/dev/null; then
    echo "   ✓ Production URLs found in build"
else
    echo "   ✗ Production URLs NOT found - using development URLs"
fi

# Start the production server
echo ""
echo "4. Starting production build server on port 3000..."
echo "   Open http://localhost:3000 in your browser"
echo "   Press Ctrl+C to stop"
echo ""

npx serve -s build -l 3000

