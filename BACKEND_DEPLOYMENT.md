# Backend Deployment Guide for Vercel

## Prerequisites

- ✅ Your backend code is ready (`api/index.py`)
- ✅ `requirements.txt` is updated with all dependencies
- ✅ `vercel.json` is configured correctly
- ✅ GitHub repository is connected to Vercel

## Step-by-Step Deployment

### Step 1: Prepare Your Code

Make sure you have:
- ✅ `api/index.py` - Your FastAPI application
- ✅ `api/vercel_handler.py` - Vercel handler (already created)
- ✅ `requirements.txt` - Python dependencies (already updated)
- ✅ `vercel.json` - Vercel configuration (already updated)

### Step 2: Commit and Push Changes

If you haven't already, commit the new files:

```bash
git add api/vercel_handler.py requirements.txt vercel.json
git commit -m "Add Vercel deployment configuration for backend"
git push origin main
```

### Step 3: Deploy on Vercel

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/dashboard
   - Sign in with your GitHub account

2. **Create New Project**
   - Click **"Add New..."** → **"Project"**
   - Or click **"Import Project"**

3. **Import Repository**
   - Find and select: `vinitha-harith/The-AI-Engineer-Challenge`
   - Click **"Import"**

4. **Configure Project Settings**
   
   **Important Settings:**
   - **Framework Preset**: Select **"Other"**
   - **Root Directory**: Leave **empty** (deploy from root)
   - **Build Command**: Leave **empty** (Vercel will auto-detect)
   - **Output Directory**: Leave **empty**
   - **Install Command**: `pip install -r requirements.txt`
   - **Python Version**: `3.12` (or leave default)

5. **Add Environment Variables**
   - Click **"Environment Variables"**
   - Add:
     - **Name**: `OPENAI_API_KEY`
     - **Value**: Your OpenAI API key (starts with `sk-...`)
     - **Environment**: Select all (Production, Preview, Development)
   - Click **"Save"**

6. **Deploy!**
   - Click **"Deploy"**
   - Wait for build to complete (usually 1-2 minutes)

### Step 4: Get Your Backend URL

After deployment completes:

1. Vercel will show a success message
2. Click on the deployment or project name
3. You'll see a URL like: `https://your-project-name-xyz123.vercel.app`
4. **This is your BACKEND URL** - Copy it!

Example backend URL:
```
https://the-ai-engineer-challenge-api-abc123.vercel.app
```

### Step 5: Test Your Backend

Test that your backend is working:

1. **Test root endpoint:**
   ```bash
   curl https://your-backend-url.vercel.app/
   ```
   Should return: `{"status": "ok"}`

2. **Test chat endpoint:**
   ```bash
   curl https://your-backend-url.vercel.app/api/chat \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}'
   ```
   Should return: `{"reply": "..."}`

   **Note**: This will use your OpenAI API key, so it will make a real API call!

### Step 6: Update Frontend Configuration

Now that you have your backend URL:

1. **Update Environment Variable in Frontend Project:**
   - Go to your **frontend project** in Vercel Dashboard
   - Settings → Environment Variables
   - Add/Update: `NEXT_PUBLIC_API_URL` = `https://your-backend-url.vercel.app`
   - Redeploy frontend

2. **OR Update vercel.json:**
   - Update `frontend/vercel.json` with your backend URL
   - Commit and push (auto-redeploys)

## Troubleshooting

### Build Fails

**Error: Module not found**
- Check `requirements.txt` has all dependencies
- Make sure `mangum` is included

**Error: Import error**
- Verify `api/vercel_handler.py` exists
- Check import paths are correct

**Error: OPENAI_API_KEY not configured**
- Make sure environment variable is set in Vercel
- Check it's set for the correct environment (Production/Preview)

### Deployment Succeeds But API Doesn't Work

1. **Check Function Logs:**
   - Go to Vercel Dashboard → Your Project → Deployments
   - Click on the deployment → "Functions" tab
   - Check logs for errors

2. **Test the endpoint:**
   ```bash
   curl https://your-backend-url.vercel.app/
   ```

3. **Verify environment variables:**
   - Settings → Environment Variables
   - Make sure `OPENAI_API_KEY` is set

### 500 Errors

- Check Vercel function logs for detailed error messages
- Verify OpenAI API key is valid
- Check OpenAI API quota/billing

## Project Structure

After deployment, your project should have:

```
The-AI-Engineer-Challenge/
├── api/
│   ├── index.py              # FastAPI app
│   └── vercel_handler.py     # Vercel handler
├── requirements.txt          # Python dependencies
└── vercel.json              # Vercel configuration
```

## Next Steps

Once backend is deployed:

1. ✅ Note your backend URL
2. ✅ Update frontend environment variable
3. ✅ Test the full stack (frontend → backend → OpenAI)
4. ✅ Share your deployed app!

## Quick Reference

- **Backend URL Format**: `https://project-name-hash.vercel.app`
- **Test Endpoint**: `https://your-backend-url.vercel.app/api/chat`
- **Environment Variable**: `OPENAI_API_KEY` (for backend)
- **Frontend Env Var**: `NEXT_PUBLIC_API_URL` (points to backend)

