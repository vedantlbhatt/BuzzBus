# How to Test BuzzBus Locally

## Quick Test (Production Build - Simulates Vercel)

1. **Start the backend:**
   ```bash
   cd BuzzBus.Api
   dotnet run --urls "http://localhost:5001"
   ```

2. **In a new terminal, run the test script:**
   ```bash
   ./test-locally.sh
   ```

   Or manually:
   ```bash
   npm run build
   npx serve -s build -l 3000
   ```

3. **Open your browser:**
   - Go to `http://localhost:3000`
   - Open Developer Tools (F12 or Cmd+Option+I)
   - Check the **Console** tab for errors
   - Check the **Network** tab to see API calls

## Development Test

1. **Start the backend:**
   ```bash
   cd BuzzBus.Api
   dotnet run --urls "http://localhost:5001"
   ```

2. **In a new terminal, start the frontend:**
   ```bash
   npm start
   ```

3. **Open your browser:**
   - Go to `http://localhost:3000`
   - Open Developer Tools (F12 or Cmd+Option+I)

## What to Check

### In the Console Tab:
- Look for errors like:
  - `Failed to load buildings`
  - `Failed to load map data`
  - `CORS error`
  - `Network error`
- Check the detailed error messages (the code logs them)

### In the Network Tab:
1. Filter by "Fetch/XHR"
2. Look for API calls to:
   - `/api/buildings` (or `https://buzzbus-production.up.railway.app/api/buildings`)
   - `/api/RouteSearch/map-routes`
   - `/api/RouteSearch/map-vehicles`
3. Click on each request to see:
   - **Status**: Should be 200 (OK)
   - **Response**: Should show the data
   - **Headers**: Check for CORS headers

### What Should Work:
- ✅ Buildings dropdown should populate
- ✅ Map should load with routes and vehicles
- ✅ Route search should work

### If It Doesn't Work:
- Check the Console for the exact error message
- Check the Network tab to see which API call failed
- Check the Response tab to see what the server returned
- Check if the backend is actually running on port 5001

## Testing Production URLs

To test if the production API URLs work:

```bash
# Test buildings endpoint
curl https://buzzbus-production.up.railway.app/api/buildings

# Test map routes endpoint
curl https://buzzbus-production.up.railway.app/api/RouteSearch/map-routes

# Test map vehicles endpoint
curl https://buzzbus-production.up.railway.app/api/RouteSearch/map-vehicles
```

All should return JSON data.

