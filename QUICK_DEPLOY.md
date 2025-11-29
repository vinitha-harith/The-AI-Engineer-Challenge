# Quick Deploy: Frontend (Vercel) + Backend (Render)

## 🚀 5-Minute Setup

### Step 1: Deploy Backend to Render (3 min)

1. **Go to Render**: https://render.com
2. **Sign up** with GitHub (free)
3. **New Web Service** → Connect repo: `vinitha-harith/The-AI-Engineer-Challenge`
4. **Settings:**
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn api.index:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables:**
   - `OPENAI_API_KEY` = your key
   - `RESTRICT_CORS` = `false`
6. **Deploy** → Copy URL (e.g., `https://mental-coach-backend.onrender.com`)

### Step 2: Connect Frontend (2 min)

1. **Vercel Dashboard** → Your Frontend Project
2. **Settings** → Environment Variables
3. **Add:** `NEXT_PUBLIC_API_URL` = Your Render backend URL
4. **Redeploy** frontend

### Step 3: Test ✅

- Frontend: `https://the-ai-engineer-challenge-rouge-eta.vercel.app`
- Backend: `https://your-backend.onrender.com`
- Send a message → Should work!

## 📋 What You Get

- ✅ Frontend: Publicly accessible on Vercel
- ✅ Backend: Publicly accessible on Render
- ✅ HTTPS: Secure connections
- ✅ Free: Both services have free tiers

## 🆘 Troubleshooting

**Backend not working?**
- Check Render logs
- Verify `OPENAI_API_KEY` is set

**Frontend can't connect?**
- Check `NEXT_PUBLIC_API_URL` is set
- Verify backend URL is correct

**CORS errors?**
- Set `RESTRICT_CORS=false` in Render
- Redeploy backend

## 📚 Full Guides

- **Render**: See `DEPLOY_BACKEND_RENDER.md`
- **Railway**: See `DEPLOY_BACKEND_RAILWAY.md`
- **Complete Solution**: See `COMPLETE_DEPLOYMENT_SOLUTION.md`

