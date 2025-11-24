# Deployment Configuration Check

## ✅ Configuration Summary

### Backend (FastAPI on Railway)
- **Production URL**: `https://buzzbus-production.up.railway.app`
- **Local Development**: `http://localhost:5000`
- **CORS**: Configured for localhost and Vercel deployments
- **Port**: Uses `PORT` environment variable (Railway sets automatically)

### Frontend (React on Vercel)
- **Local Development**: `http://localhost:3000` (uses proxy to backend)
- **Production**: Automatically detects environment and uses Railway backend
- **Proxy**: Configured in `package.json` for local development

## 🔧 API URL Detection

The frontend automatically detects the environment:

```javascript
// Local development (localhost or 127.0.0.1)
→ Uses proxy: '/api/RouteSearch' (proxies to http://localhost:5000)

// Production (Vercel)
→ Uses Railway: 'https://buzzbus-production.up.railway.app/api/RouteSearch'
```

## ✅ CORS Configuration

Backend allows:
- `http://localhost:3000` (local dev)
- `http://localhost:3001` (alternate port)
- `http://127.0.0.1:3000` (local dev)
- `https://buzz-bus.vercel.app` (Vercel)
- `https://buzzbus.vercel.app` (Vercel)
- `https://*.vercel.app` (all Vercel preview deployments via regex)

## 🚀 Deployment Checklist

### Railway (Backend)
- [x] Root directory set to `backend/`
- [x] `PORT` environment variable (auto-set by Railway)
- [x] `TRANSLOC_API_KEY` environment variable set
- [x] CORS configured for Vercel domains
- [x] Health endpoint: `/api/health`

### Vercel (Frontend)
- [x] Build command: `npm run build`
- [x] Output directory: `build`
- [x] Environment detection for API URLs
- [x] No environment variables needed (uses Railway URL in production)

## 🧪 Testing

### Local Development
1. Start backend: `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 5000`
2. Start frontend: `npm start`
3. Frontend proxies API calls to backend automatically

### Production
1. Backend deployed on Railway at `https://buzzbus-production.up.railway.app`
2. Frontend deployed on Vercel
3. Frontend automatically uses Railway URL in production

## 🔍 Verification Commands

```bash
# Test backend health
curl https://buzzbus-production.up.railway.app/api/health

# Test backend route search (local)
curl -X POST http://localhost:5000/api/RouteSearch \
  -H "Content-Type: application/json" \
  -d '{"begin_location": "Tech Tower", "dest_location": "Student Center"}'

# Test backend route search (production)
curl -X POST https://buzzbus-production.up.railway.app/api/RouteSearch \
  -H "Content-Type: application/json" \
  -d '{"begin_location": "Tech Tower", "dest_location": "Student Center"}'
```

## 📝 Notes

- The frontend uses environment detection, so no environment variables are needed
- The proxy in `package.json` only works in development (Create React App)
- In production, Vercel serves static files, so API calls go directly to Railway
- CORS is properly configured to allow Vercel → Railway requests



