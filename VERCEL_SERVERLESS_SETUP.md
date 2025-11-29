# Vercel Serverless Function Setup for FastAPI

## ✅ Configuration Complete

Your FastAPI backend is now configured to run as a Vercel serverless function.

## 📁 File Structure

```
The-AI-Engineer-Challenge/
├── api/
│   ├── index.py              # FastAPI application
│   └── vercel_handler.py     # Vercel serverless function handler
├── vercel.json               # Vercel configuration
└── requirements.txt          # Python dependencies (includes mangum)
```

## 🔧 Vercel Configuration

### vercel.json

```json
{
  "version": 2,
  "functions": {
    "api/*.py": {
      "runtime": "python3.12",
      "maxDuration": 10,
      "memory": 1024
    }
  },
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/vercel_handler.py"
    }
  ]
}
```

**Configuration Details:**
- `runtime`: Python 3.12
- `maxDuration`: 10 seconds (max execution time)
- `memory`: 1024 MB (1 GB)
- `routes`: All requests (`/*`) route to the handler

## 🚀 Vercel Deployment Steps

### Step 1: Prepare Repository

1. **Ensure all files are committed:**
   ```bash
   git add .
   git commit -m "Configure FastAPI as Vercel serverless function"
   git push origin main
   ```

### Step 2: Deploy to Vercel

1. **Go to Vercel Dashboard:**
   - Visit: https://vercel.com/dashboard
   - Sign in with GitHub

2. **Create New Project:**
   - Click "Add New..." → "Project"
   - Import repository: `vinitha-harith/The-AI-Engineer-Challenge`

3. **Configure Project Settings:**
   - **Framework Preset**: Select **"Other"**
   - **Root Directory**: Leave empty (root `/`)
   - **Build Command**: Leave empty (Vercel auto-detects)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

4. **Add Environment Variables:**
   - Click "Environment Variables"
   - Add:
     - **Name**: `OPENAI_API_KEY`
     - **Value**: Your OpenAI API key
     - **Environments**: Production, Preview, Development (select all)
   - Add (optional):
     - **Name**: `FRONTEND_URL`
     - **Value**: `https://the-ai-engineer-challenge-rouge-eta.vercel.app`
     - **Environments**: Production, Preview, Development
   - Add (optional):
     - **Name**: `RESTRICT_CORS`
     - **Value**: `false` (for public access)
     - **Environments**: Production, Preview, Development

5. **Deploy:**
   - Click "Deploy"
   - Wait 2-3 minutes for build and deployment
   - **Copy the deployment URL** (e.g., `https://your-project-xyz123.vercel.app`)

### Step 3: Connect Frontend

1. **Go to Frontend Project in Vercel:**
   - Find your frontend project
   - Settings → Environment Variables

2. **Add Backend URL:**
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: Your backend Vercel URL (from Step 2)
   - Example: `https://your-project-xyz123.vercel.app`
   - **Environments**: Production, Preview, Development (all)

3. **Redeploy Frontend:**
   - Go to Deployments tab
   - Click "Redeploy" on latest deployment
   - Or push a new commit to trigger redeploy

### Step 4: Test

1. **Test Backend:**
   ```bash
   curl https://your-backend.vercel.app/
   # Should return: {"status":"ok"}
   ```

2. **Test API Endpoint:**
   ```bash
   curl -X POST https://your-backend.vercel.app/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}'
   ```

3. **Test Frontend:**
   - Open: `https://the-ai-engineer-challenge-rouge-eta.vercel.app`
   - Send a message
   - Should work! ✅

## 🔍 How It Works

1. **Request comes in** → Vercel routes to `/api/vercel_handler.py`
2. **Handler receives request** → Mangum converts it to ASGI format
3. **FastAPI processes** → Handles the request
4. **Response returned** → Mangum converts back to Vercel format

## 📋 Environment Variables Summary

### Backend (Vercel Serverless Function)

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key

**Optional:**
- `FRONTEND_URL` - Frontend URL for CORS (if restricting)
- `RESTRICT_CORS` - Set to `false` for public access (default)

### Frontend (Vercel Next.js)

**Required:**
- `NEXT_PUBLIC_API_URL` - Your backend Vercel URL

## 🧪 Testing Locally

You can test the serverless function locally with Vercel CLI:

```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Run locally
vercel dev

# Test
curl http://localhost:3000/
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## 🐛 Troubleshooting

### Build Fails

**Error: Module not found**
- Check `requirements.txt` includes all dependencies
- Verify `mangum` is included

**Error: Import error**
- Verify `api/vercel_handler.py` exists
- Check import path: `from index import app`

### Function Timeout

**Error: Function execution exceeded timeout**
- Increase `maxDuration` in `vercel.json` (max 60s on Pro plan)
- Optimize your code
- Check OpenAI API response time

### CORS Errors

1. **Set environment variable:**
   - `RESTRICT_CORS` = `false` (for public access)
   - Or set `FRONTEND_URL` to your frontend URL

2. **Redeploy backend**

### 500 Errors

1. **Check Function Logs:**
   - Vercel Dashboard → Your Project → Deployments
   - Click on deployment → Functions tab
   - Check logs for errors

2. **Verify Environment Variables:**
   - Ensure `OPENAI_API_KEY` is set
   - Check it's valid

## 📊 Vercel Function Limits

**Free Tier:**
- 100 GB-hours execution time/month
- 10 second max duration
- 1024 MB memory (1 GB)

**Pro Tier ($20/month):**
- 1000 GB-hours execution time/month
- 60 second max duration
- Up to 3008 MB memory

## ✅ Checklist

- [x] `vercel.json` configured with functions settings
- [x] `api/vercel_handler.py` handler created
- [x] `requirements.txt` includes `mangum`
- [ ] Backend deployed to Vercel
- [ ] `OPENAI_API_KEY` set in Vercel
- [ ] `NEXT_PUBLIC_API_URL` set in frontend
- [ ] Frontend redeployed
- [ ] Tested backend endpoint
- [ ] Tested frontend connection

## 🎯 Next Steps

1. ✅ Deploy backend to Vercel
2. ✅ Set environment variables
3. ✅ Connect frontend
4. ✅ Test the full stack
5. 🎉 Your app is live!

