# Deployment Guide: Frontend & Backend on Vercel

## Current Project Structure

Your project has:
- **Backend**: FastAPI app in `/api/index.py`
- **Frontend**: Next.js app in `/frontend/`
- **Root vercel.json**: Routes to `/api/index.py` (for backend-only deployment)
- **Frontend vercel.json**: Has placeholder backend URL (for separate deployments)

## Two Deployment Options

### Option 1: Separate Deployments (Recommended)

Deploy the frontend and backend as **two separate Vercel projects**. This is the most flexible approach.

#### Backend Deployment

1. **Deploy the backend separately:**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New Project"
   - Import the repository
   - **Root Directory**: Set to the repo root (or create a separate repo for backend)
   - **Framework Preset**: Select "Other" (for Python/FastAPI)
   - **Build Command**: Leave empty or set to `pip install -r requirements.txt`
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

2. **Set Environment Variables:**
   - Go to Project Settings → Environment Variables
   - Add: `OPENAI_API_KEY` = your OpenAI API key

3. **Configure vercel.json for backend:**
   - The root `vercel.json` should work, but you may need:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "api/index.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "api/index.py"
       }
     ]
   }
   ```

4. **Deploy and note the backend URL:**
   - After deployment, you'll get a URL like: `https://your-backend-name.vercel.app`
   - This is your **BACKEND URL**

#### Frontend Deployment

1. **Deploy the frontend:**
   - Go to Vercel Dashboard
   - Click "Add New Project"
   - Import the same repository (or a separate frontend repo)
   - **Root Directory**: Set to `frontend`
   - **Framework Preset**: Select "Next.js"
   - Vercel will auto-detect Next.js settings

2. **Set Environment Variables:**
   - Go to Project Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` = `https://your-backend-name.vercel.app`
   - (Replace with your actual backend URL from step above)

3. **Update frontend/vercel.json:**
   - Update the destination URL to your backend URL:
   ```json
   {
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "https://your-backend-name.vercel.app/api/:path*"
       }
     ]
   }
   ```

4. **Deploy**
   - Your frontend will be available at: `https://your-frontend-name.vercel.app`

---

### Option 2: Monorepo Deployment (Alternative)

Deploy everything as a single Vercel project. This requires more configuration.

#### Steps:

1. **Create a single vercel.json at root:**
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "api/index.py",
         "use": "@vercel/python"
       },
       {
         "src": "frontend/package.json",
         "use": "@vercel/next"
       }
     ],
     "routes": [
       {
         "src": "/api/(.*)",
         "dest": "api/index.py"
       },
       {
         "src": "/(.*)",
         "dest": "frontend/$1"
       }
     ]
   }
   ```

2. **Set Environment Variables:**
   - `OPENAI_API_KEY` for backend
   - `NEXT_PUBLIC_API_URL` for frontend (can be relative or absolute)

3. **Root Directory:** Leave empty (root of repo)

4. **Framework Preset:** "Other"

This approach is more complex and less flexible than separate deployments.

---

## Recommended: Separate Deployments

**I recommend Option 1 (Separate Deployments)** because:
- ✅ Easier to manage and debug
- ✅ Independent scaling
- ✅ Can update frontend/backend separately
- ✅ Clearer separation of concerns
- ✅ Better for production applications

---

## Finding Your Backend URL

If you've already deployed the backend:

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Find your backend project
3. Click on it
4. Look at the "Domains" section
5. You'll see a URL like: `https://project-name.vercel.app`
6. **This is your backend URL** - use it in:
   - `NEXT_PUBLIC_API_URL` environment variable
   - `frontend/vercel.json` destination URL

---

## Current Status Check

To check what you currently have deployed:

1. **Check Vercel Dashboard:**
   - How many projects do you see?
   - What are their names?
   - What URLs do they have?

2. **Your frontend URL:** `https://the-ai-engineer-challenge-rouge-eta.vercel.app/`
   - This suggests your frontend is deployed

3. **Do you have a separate backend deployment?**
   - Check Vercel Dashboard for another project
   - Or check if the backend is working at your frontend URL + `/api/chat`

---

## Quick Setup Checklist

### Backend:
- [ ] Deploy backend as separate Vercel project
- [ ] Set `OPENAI_API_KEY` environment variable
- [ ] Note the backend URL (e.g., `https://mental-coach-api.vercel.app`)

### Frontend:
- [ ] Deploy frontend as separate Vercel project (or update existing)
- [ ] Set `NEXT_PUBLIC_API_URL` environment variable = your backend URL
- [ ] Update `frontend/vercel.json` with backend URL
- [ ] Redeploy frontend

---

## Testing

After deployment:

1. Test backend directly:
   ```bash
   curl https://your-backend-url.vercel.app/api/chat \
     -X POST \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}'
   ```

2. Test frontend:
   - Open `https://your-frontend-url.vercel.app`
   - Try sending a message
   - Check browser console (F12) → Network tab
   - Verify POST requests go to correct backend URL

---

## Troubleshooting

**Frontend can't reach backend:**
- Verify `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- Check `frontend/vercel.json` has correct backend URL
- Hard refresh browser (Cmd+Shift+R)

**Backend errors:**
- Check `OPENAI_API_KEY` is set in Vercel backend project
- Check Vercel function logs for errors

**CORS errors:**
- Backend already allows all origins (`*`)
- If issues persist, check backend CORS configuration

