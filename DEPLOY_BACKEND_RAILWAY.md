# Deploy Backend to Railway (Alternative to Render)

## Why Railway?

- ✅ **$5 free credit monthly** - Good for development
- ✅ **No automatic spin-down** - Always available
- ✅ **Easy deployment** - Connect GitHub and deploy
- ✅ **Automatic HTTPS** - Secure connections
- ✅ **Better for production** - More reliable than free Render

## Step-by-Step Deployment

### Step 1: Sign Up

1. **Go to Railway:**
   - Visit: https://railway.app
   - Sign up with GitHub (free)

### Step 2: Create New Project

1. **New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose: `vinitha-harith/The-AI-Engineer-Challenge`

### Step 3: Configure Service

1. **Railway will auto-detect Python:**
   - It should detect `requirements.txt`
   - If not, set:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn api.index:app --host 0.0.0.0 --port $PORT`

2. **Add Environment Variables:**
   - Click on your service → Variables tab
   - Add:
     - `OPENAI_API_KEY` = Your OpenAI API key
     - `FRONTEND_URL` = `https://the-ai-engineer-challenge-rouge-eta.vercel.app` (optional)
     - `RESTRICT_CORS` = `false` (for public access)

3. **Generate Domain:**
   - Click "Settings" → "Generate Domain"
   - Railway will give you a URL like: `your-service.up.railway.app`
   - **Copy this URL** - this is your backend URL

### Step 4: Connect Frontend

1. **In Vercel Dashboard:**
   - Frontend Project → Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` = Your Railway backend URL
   - Redeploy frontend

### Step 5: Test

```bash
# Test backend
curl https://your-service.up.railway.app/
# Should return: {"status":"ok"}
```

## Railway Pricing

- **Free**: $5 credit/month (usually enough for development)
- **Hobby**: $5/month (if you exceed free credit)
- **Pro**: $20/month (for production)

## Advantages Over Render Free Tier

- ✅ No 15-minute spin-down
- ✅ Faster cold starts
- ✅ More reliable for production
- ✅ Better monitoring

