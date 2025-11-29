# Deploy Backend to Render (Free Python Hosting)

## Why Render?

- ✅ **Free tier available** - Perfect for development
- ✅ **Native Python support** - No configuration needed
- ✅ **Automatic HTTPS** - Secure connections
- ✅ **Public access** - Accessible from anywhere
- ✅ **Easy deployment** - Connect GitHub and deploy

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Make sure your code is pushed to GitHub:**
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Files needed (already created):**
   - ✅ `api/index.py` - Your FastAPI app
   - ✅ `requirements.txt` - Python dependencies
   - ✅ `render.yaml` - Render configuration

### Step 2: Deploy to Render

1. **Sign up/Login to Render:**
   - Go to: https://render.com
   - Sign up with GitHub (free)

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `vinitha-harith/The-AI-Engineer-Challenge`

3. **Configure Service:**
   - **Name**: `mental-coach-backend` (or any name)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty (root `/`)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.index:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables:**
   - Click "Advanced" → "Add Environment Variable"
   - Add:
     - **Key**: `OPENAI_API_KEY`
     - **Value**: Your OpenAI API key
   - Add (optional):
     - **Key**: `FRONTEND_URL`
     - **Value**: `https://the-ai-engineer-challenge-rouge-eta.vercel.app`
   - Add:
     - **Key**: `RESTRICT_CORS`
     - **Value**: `false` (for public access)

5. **Deploy:**
   - Click "Create Web Service"
   - Wait 2-3 minutes for deployment
   - **Copy the service URL** (e.g., `https://mental-coach-backend.onrender.com`)

### Step 3: Connect Frontend to Backend

1. **Go to Vercel Dashboard:**
   - Find your frontend project
   - Settings → Environment Variables

2. **Add Backend URL:**
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: Your Render backend URL (from Step 2)
   - Example: `https://mental-coach-backend.onrender.com`
   - **Environments**: Production, Preview, Development (all)

3. **Redeploy Frontend:**
   - Go to Deployments tab
   - Click "Redeploy" on latest deployment

### Step 4: Test

1. **Test Backend:**
   ```bash
   curl https://your-backend.onrender.com/
   # Should return: {"status":"ok"}
   ```

2. **Test Frontend:**
   - Open: `https://the-ai-engineer-challenge-rouge-eta.vercel.app`
   - Send a message
   - Should work! ✅

## Render Free Tier Limits

- ✅ **Free forever** (with some limits)
- ⚠️ **Spins down after 15 minutes** of inactivity
- ⚠️ **First request after spin-down takes ~30 seconds** (cold start)
- ✅ **Unlimited requests** when active
- ✅ **512MB RAM**
- ✅ **Automatic HTTPS**

**Note:** For production, consider upgrading to paid plan ($7/month) to avoid spin-downs.

## Alternative: Railway (Similar to Render)

If you prefer Railway:

1. Go to: https://railway.app
2. New Project → Deploy from GitHub
3. Select your repository
4. Add environment variables
5. Deploy

Railway free tier:
- $5 free credit monthly
- No automatic spin-down
- Better for production

## Alternative: Fly.io (Also Good)

1. Go to: https://fly.io
2. Install flyctl CLI
3. Deploy with: `fly launch`
4. Add secrets: `fly secrets set OPENAI_API_KEY=your-key`

## Troubleshooting

### Backend Not Responding

1. **Check Render Logs:**
   - Render Dashboard → Your Service → Logs
   - Look for errors

2. **Check Environment Variables:**
   - Ensure `OPENAI_API_KEY` is set
   - Verify it's correct

3. **Check Build Logs:**
   - Render Dashboard → Your Service → Events
   - Check if build succeeded

### CORS Errors

1. **Verify CORS Settings:**
   - `RESTRICT_CORS` should be `false` for public access
   - Or set `FRONTEND_URL` to your frontend URL

2. **Check Backend Logs:**
   - Look for CORS-related errors

### Slow First Request

- This is normal on free tier (cold start)
- First request after 15 min inactivity takes ~30 seconds
- Subsequent requests are fast

## Quick Reference

**Backend URL Format:**
- Render: `https://your-service.onrender.com`
- Railway: `https://your-service.up.railway.app`
- Fly.io: `https://your-service.fly.dev`

**Environment Variables:**
- `OPENAI_API_KEY` - Required
- `FRONTEND_URL` - Optional (for CORS)
- `RESTRICT_CORS` - Optional (default: false)

**Frontend Configuration:**
- Set `NEXT_PUBLIC_API_URL` in Vercel
- Value: Your backend URL (Render/Railway/Fly.io)

