# Quick Steps to Deploy Backend & Connect Frontend

## Step 1: Deploy Backend on Vercel

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard

2. **Click "Add New Project"** or "Import Project"

3. **Import your GitHub repository:**
   - Repository: `vinitha-harith/The-AI-Engineer-Challenge`
   - Framework Preset: **Select "Other"** (for Python/FastAPI)
   - Root Directory: Leave empty (or set to root `/`)
   
4. **Configure Project Settings:**
   - **Build Command**: Leave empty (or `pip install -r requirements.txt`)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

5. **Add Environment Variable:**
   - Go to "Environment Variables"
   - Add: `OPENAI_API_KEY` = `your-openai-api-key-here`
   - Select all environments (Production, Preview, Development)

6. **Deploy!**
   - Click "Deploy"
   - Wait for deployment to complete

7. **Note the Backend URL:**
   - After deployment, Vercel will show you a URL
   - Example: `https://the-ai-engineer-challenge-api-xyz123.vercel.app`
   - **THIS IS YOUR BACKEND URL** - copy it!

---

## Step 2: Update Frontend to Use Backend URL

### Option A: Using Environment Variable (Recommended)

1. **Go to your Frontend Project in Vercel Dashboard**
   - Find the project that created `https://the-ai-engineer-challenge-rouge-eta.vercel.app`

2. **Add Environment Variable:**
   - Go to Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` = `https://your-backend-url.vercel.app`
   - (Use the backend URL from Step 1)
   - Select all environments

3. **Redeploy:**
   - Go to Deployments tab
   - Click "Redeploy" on the latest deployment
   - Or push a new commit to trigger redeploy

### Option B: Update vercel.json

Alternatively, you can update `frontend/vercel.json`:

1. **Update the file:**
   - Replace `https://your-backend-url.vercel.app` with your actual backend URL
   - Commit and push the change

2. **Vercel will auto-redeploy**

---

## Step 3: Test

1. **Test Backend Directly:**
   ```bash
   curl https://your-backend-url.vercel.app/api/chat \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}'
   ```
   Should return: `{"reply": "..."}`

2. **Test Frontend:**
   - Open: `https://the-ai-engineer-challenge-rouge-eta.vercel.app`
   - Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
   - Send a test message
   - Check browser console (F12) → Network tab
   - Verify POST request goes to your backend URL

---

## Summary

- ✅ **Backend URL**: Deploy backend first, then copy the URL Vercel gives you
- ✅ **Separate Deployment**: Yes, backend and frontend should be separate Vercel projects
- ✅ **Connection**: Use `NEXT_PUBLIC_API_URL` environment variable or update `frontend/vercel.json`

---

## If You Already Have Backend Deployed

If you've already deployed a backend but don't know the URL:

1. Go to Vercel Dashboard
2. Look for a project (might be named differently)
3. Check the "Domains" section
4. The `.vercel.app` URL is your backend URL

