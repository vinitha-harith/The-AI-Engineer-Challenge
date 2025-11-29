# Secure Frontend-Backend Integration Guide

## Overview

This guide explains how to securely connect your Vercel-deployed frontend to your FastAPI backend.

## Recommended Solution: Deploy Backend to Vercel

**Why Vercel?**
- ✅ Automatic HTTPS (secure connection)
- ✅ No port forwarding needed
- ✅ Built-in security
- ✅ Easy environment variable management
- ✅ Free tier available

## Step-by-Step Deployment

### Step 1: Deploy Backend to Vercel

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard

2. **Create New Project**:
   - Click "Add New..." → "Project"
   - Import repository: `vinitha-harith/The-AI-Engineer-Challenge`
   - **Framework Preset**: Select "Other"
   - **Root Directory**: Leave empty (root `/`)
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

3. **Add Environment Variables**:
   - Go to "Environment Variables"
   - Add:
     - **Name**: `OPENAI_API_KEY`
     - **Value**: Your OpenAI API key
     - **Environments**: Production, Preview, Development (all)
   - Add (optional):
     - **Name**: `FRONTEND_URL`
     - **Value**: Your frontend Vercel URL (e.g., `https://the-ai-engineer-challenge-rouge-eta.vercel.app`)
     - **Environments**: Production, Preview, Development

4. **Deploy**:
   - Click "Deploy"
   - Wait for deployment to complete
   - **Note the backend URL** (e.g., `https://your-backend-xyz123.vercel.app`)

### Step 2: Update Frontend to Use Backend URL

1. **Go to Frontend Project in Vercel**:
   - Find your frontend project
   - Go to Settings → Environment Variables

2. **Add Backend URL**:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: Your backend Vercel URL (from Step 1)
   - Example: `https://your-backend-xyz123.vercel.app`
   - **Environments**: Production, Preview, Development (all)

3. **Redeploy Frontend**:
   - Go to Deployments tab
   - Click "Redeploy" on latest deployment
   - Or push a new commit to trigger redeploy

### Step 3: Update Backend CORS (Optional but Recommended)

After deploying, update the backend to restrict CORS to your frontend domain:

1. **In Vercel Backend Project**:
   - Settings → Environment Variables
   - Add/Update: `FRONTEND_URL` = Your frontend Vercel URL

2. **The backend code already supports this** - it will automatically use `FRONTEND_URL` if set.

## Alternative Solutions

### Option 2: Use ngrok (Temporary/Development Only)

⚠️ **Not recommended for production** - Use only for testing.

```bash
# Install ngrok
brew install ngrok

# Start your backend locally
uv run uvicorn api.index:app --host 0.0.0.0 --port 8000 --reload

# In another terminal, create tunnel
ngrok http 8000

# Use the ngrok HTTPS URL (e.g., https://abc123.ngrok.io)
# Set NEXT_PUBLIC_API_URL in Vercel to this URL
```

**Limitations:**
- Free tier has URL changes on restart
- Not secure for production
- Rate limits

### Option 3: Cloudflare Tunnel (More Secure)

1. Install Cloudflare Tunnel
2. Create tunnel
3. Route traffic to localhost:8000
4. Get persistent HTTPS URL
5. Use in `NEXT_PUBLIC_API_URL`

### Option 4: AWS/GCP/Azure (For Production Scale)

For enterprise/production:
- Deploy backend to AWS Lambda, GCP Cloud Run, or Azure Functions
- Use API Gateway for HTTPS
- Set up proper authentication

## Security Best Practices

### ✅ Implemented in Code

1. **CORS Configuration**: Backend restricts origins (configurable)
2. **Error Handling**: Frontend handles errors gracefully
3. **HTTPS**: Automatic with Vercel deployment
4. **Environment Variables**: Secrets stored securely in Vercel

### 🔒 Additional Recommendations

1. **Add API Authentication**:
   ```python
   # In api/index.py, add API key validation
   API_KEY = os.getenv("API_KEY")
   
   @app.middleware("http")
   async def verify_api_key(request: Request, call_next):
       if request.url.path.startswith("/api/"):
           api_key = request.headers.get("X-API-Key")
           if api_key != API_KEY:
               return JSONResponse({"detail": "Unauthorized"}, status_code=401)
       return await call_next(request)
   ```

2. **Rate Limiting**: Add rate limiting to prevent abuse
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/api/chat")
   @limiter.limit("10/minute")
   def chat(request: Request, ...):
       ...
   ```

3. **Input Validation**: Already implemented with Pydantic

4. **Monitor Usage**: Track API calls to detect abuse

## Testing the Integration

### 1. Test Backend Directly

```bash
# Test backend health
curl https://your-backend.vercel.app/

# Test chat endpoint
curl -X POST https://your-backend.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

### 2. Test Frontend Connection

1. Open your frontend URL: `https://your-frontend.vercel.app`
2. Open browser DevTools (F12) → Network tab
3. Send a message
4. Check:
   - Request goes to backend URL
   - Status is 200 (OK)
   - Response contains chat reply

### 3. Check for CORS Errors

If you see CORS errors in browser console:
- Verify `FRONTEND_URL` is set in backend environment variables
- Check backend CORS configuration
- Ensure frontend URL matches exactly (including https://)

## Troubleshooting

### Frontend can't connect to backend

1. **Check Environment Variable**:
   - Verify `NEXT_PUBLIC_API_URL` is set in Vercel
   - Must start with `https://` (not `http://`)
   - No trailing slash

2. **Check Backend Status**:
   - Visit backend URL directly
   - Should return: `{"status": "ok"}`

3. **Check Browser Console**:
   - Look for CORS errors
   - Check Network tab for failed requests

### CORS Errors

1. **Update Backend CORS**:
   - Set `FRONTEND_URL` environment variable in backend
   - Redeploy backend
   - Or update `api/index.py` to include your frontend URL

2. **Verify URLs Match**:
   - Frontend URL must exactly match what's in CORS config
   - Include protocol (`https://`)
   - No trailing slashes

### Backend Returns 500 Errors

1. **Check Backend Logs**:
   - Vercel Dashboard → Your Backend Project → Deployments
   - Click on deployment → Functions tab
   - Check logs for errors

2. **Verify Environment Variables**:
   - Ensure `OPENAI_API_KEY` is set
   - Check it's valid

## Quick Reference

### Environment Variables Needed

**Backend (Vercel):**
- `OPENAI_API_KEY` - Your OpenAI API key
- `FRONTEND_URL` (optional) - Frontend URL for CORS

**Frontend (Vercel):**
- `NEXT_PUBLIC_API_URL` - Backend Vercel URL

### URLs Format

- ✅ Correct: `https://your-backend.vercel.app`
- ❌ Wrong: `http://your-backend.vercel.app` (no HTTPS)
- ❌ Wrong: `https://your-backend.vercel.app/` (trailing slash)

## Next Steps

1. ✅ Deploy backend to Vercel
2. ✅ Set `NEXT_PUBLIC_API_URL` in frontend
3. ✅ Test the connection
4. 🔒 Add authentication (optional but recommended)
5. 📊 Monitor usage and add rate limiting

