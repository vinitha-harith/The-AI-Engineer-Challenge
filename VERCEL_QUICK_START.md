# Vercel Serverless Function - Quick Start

## ✅ Configuration Complete

Your FastAPI is configured as a Vercel serverless function. Here's what was set up:

## 📁 Files Configured

1. **`vercel.json`** - Updated with functions configuration
2. **`api/vercel_handler.py`** - Serverless function handler (uses Mangum)
3. **`requirements.txt`** - Includes `mangum` for Vercel compatibility
4. **Frontend** - Already configured to work with backend

## 🚀 Deploy to Vercel

### Option A: Same Project (Frontend + Backend)

If deploying frontend and backend in the **same Vercel project**:

1. **Deploy:**
   - Import repo to Vercel
   - Framework: "Other"
   - Root Directory: Leave empty
   - Install Command: `pip install -r requirements.txt`
   - Add `OPENAI_API_KEY` environment variable
   - Deploy

2. **Frontend will automatically use relative paths:**
   - No `NEXT_PUBLIC_API_URL` needed
   - Frontend calls `/api/chat` which routes to serverless function

### Option B: Separate Projects (Recommended)

If deploying frontend and backend in **separate Vercel projects**:

1. **Deploy Backend:**
   - Create new project for backend
   - Framework: "Other"
   - Root Directory: Leave empty
   - Install Command: `pip install -r requirements.txt`
   - Add `OPENAI_API_KEY` environment variable
   - Deploy → Copy backend URL

2. **Connect Frontend:**
   - Frontend project → Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` = Your backend URL
   - Redeploy frontend

## 🔧 Vercel Dashboard Settings

### Project Settings

1. **General:**
   - Framework Preset: **Other**
   - Root Directory: (empty)
   - Build Command: (empty - auto-detected)
   - Output Directory: (empty)
   - Install Command: `pip install -r requirements.txt`

2. **Environment Variables:**
   - `OPENAI_API_KEY` = your OpenAI key
   - `RESTRICT_CORS` = `false` (optional, for public access)
   - `FRONTEND_URL` = your frontend URL (optional, for CORS)

### Function Settings (Auto-configured via vercel.json)

- Runtime: Python 3.12
- Max Duration: 10 seconds
- Memory: 1024 MB

## 🧪 Testing

### Test Backend

```bash
# Health check
curl https://your-backend.vercel.app/

# API endpoint
curl -X POST https://your-backend.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

### Test Frontend

1. Open your frontend URL
2. Send a message
3. Should work! ✅

## 📋 Checklist

- [x] `vercel.json` configured
- [x] `api/vercel_handler.py` handler created
- [x] `requirements.txt` includes mangum
- [ ] Deploy backend to Vercel
- [ ] Set `OPENAI_API_KEY` in Vercel
- [ ] Set `NEXT_PUBLIC_API_URL` in frontend (if separate projects)
- [ ] Test backend endpoint
- [ ] Test frontend connection

## 🆘 Troubleshooting

**Function not found:**
- Check `vercel.json` routes point to `/api/vercel_handler.py`
- Verify file exists at `api/vercel_handler.py`

**Import errors:**
- Check `requirements.txt` includes all dependencies
- Verify `mangum` is included

**Timeout errors:**
- Increase `maxDuration` in `vercel.json` (max 60s on Pro)

See `VERCEL_SERVERLESS_SETUP.md` for detailed troubleshooting.

