# Quick Start: Deploy Backend to Vercel

## ✅ What I've Prepared

I've already configured everything you need:

1. ✅ `api/vercel_handler.py` - Vercel-compatible handler
2. ✅ `vercel.json` - Updated with proper build configuration  
3. ✅ `requirements.txt` - Added `mangum` for Lambda compatibility

## 🚀 Deploy in 5 Steps

### Step 1: Commit Changes
```bash
cd /Users/vharith/Desktop/AI_MS/AI_Challenge/The-AI-Engineer-Challenge
git add api/vercel_handler.py requirements.txt vercel.json
git commit -m "Add Vercel deployment configuration for backend"
git push origin main
```

### Step 2: Go to Vercel Dashboard
- Visit: https://vercel.com/dashboard
- Sign in with GitHub

### Step 3: Import Project
- Click **"Add New..."** → **"Project"**
- Select repository: `vinitha-harith/The-AI-Engineer-Challenge`
- Click **"Import"**

### Step 4: Configure Settings

**Important Settings:**
- **Framework Preset**: `Other`
- **Root Directory**: Leave empty (root `/`)
- **Install Command**: `pip install -r requirements.txt`
- Everything else: Leave as default

**Add Environment Variable:**
- Click **"Environment Variables"**
- Add:
  - Name: `OPENAI_API_KEY`
  - Value: `your-openai-api-key-here`
  - Environments: Check all (Production, Preview, Development)
- Click **"Save"**

### Step 5: Deploy!
- Click **"Deploy"**
- Wait 1-2 minutes
- **Copy the URL** Vercel gives you (this is your backend URL!)

## 🎯 After Deployment

1. **Your backend URL will be something like:**
   ```
   https://the-ai-engineer-challenge-xyz123.vercel.app
   ```

2. **Test it:**
   ```bash
   curl https://your-backend-url.vercel.app/
   ```
   Should return: `{"status": "ok"}`

3. **Update your frontend:**
   - Go to your **frontend project** in Vercel
   - Add environment variable: `NEXT_PUBLIC_API_URL` = your backend URL
   - Redeploy frontend

## 📚 Full Guide

For detailed instructions and troubleshooting, see: `BACKEND_DEPLOYMENT.md`

---

**Ready? Start with Step 1 above!** 🚀

