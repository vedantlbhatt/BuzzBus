# Railway Deployment Guide for FastAPI Backend

## Quick Answer: Yes, you can just change the directory!

Railway tracks the **root directory** of your project. You need to:

1. **Change Railway's root directory** from `BuzzBus.Api` to `backend`
2. **That's it!** Railway will auto-detect Python and use the Dockerfile

---

## Step-by-Step Instructions

### 1. In Railway Dashboard:

1. Go to your Railway project
2. Click on your service (the one running .NET)
3. Go to **Settings** tab
4. Find **Root Directory** setting
5. Change from: `BuzzBus.Api` 
6. Change to: `backend`
7. Save changes

### 2. Railway Will Automatically:

- ✅ Detect it's a Python project
- ✅ Use the `Dockerfile` in `backend/` directory
- ✅ Install dependencies from `requirements.txt`
- ✅ Run `uvicorn main:app` (from Dockerfile CMD)
- ✅ Set `PORT` environment variable automatically

### 3. Environment Variables:

Make sure these are set in Railway:
- `TRANSLOC_API_KEY` - Your Transloc API key
- `TRANSLOC_BASE_URL` - `https://gatech.transloc.com/Services/JSONPRelay.svc`
- `PORT` - Railway sets this automatically (don't set manually)

### 4. That's It!

Railway will:
- Build the Docker image
- Deploy FastAPI
- Your API will be live at the same URL: `https://buzzbus-production.up.railway.app`

---

## What Happens:

**Before:**
```
Railway Root: BuzzBus.Api/
  → Builds .NET
  → Runs: dotnet BuzzBus.Api.dll
```

**After:**
```
Railway Root: backend/
  → Builds Python (Dockerfile)
  → Runs: uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Verification:

After deployment, test:
```bash
curl https://buzzbus-production.up.railway.app/api/health
# Should return: {"status":"healthy"}
```

---

## Notes:

- ✅ No need to change frontend URLs (they already point to Railway)
- ✅ Same domain, just different backend
- ✅ FastAPI endpoints match .NET endpoints exactly
- ✅ Response format is identical (camelCase)

---

## If Something Goes Wrong:

1. Check Railway logs
2. Verify environment variables are set
3. Make sure `PORT` env var is available (Railway sets it automatically)
4. Check that `backend/Dockerfile` exists

