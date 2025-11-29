# Quick Setup: Connect Frontend to Backend

## ✅ Code Changes Made

1. **Backend CORS** - Updated to support frontend URL from environment variable
2. **Frontend Error Handling** - Improved error messages and network error handling
3. **Security** - CORS configuration allows specific origins in production

## 🚀 Quick Deployment Steps

### 1. Deploy Backend to Vercel (5 minutes)

```bash
# Already configured! Just deploy:
```

1. Go to https://vercel.com/dashboard
2. Click "Add New Project"
3. Import: `vinitha-harith/The-AI-Engineer-Challenge`
4. Settings:
   - Framework: **Other**
   - Root Directory: (empty)
   - Install Command: `pip install -r requirements.txt`
5. Environment Variables:
   - `OPENAI_API_KEY` = your OpenAI key
   - `FRONTEND_URL` = `https://the-ai-engineer-challenge-rouge-eta.vercel.app` (your frontend URL)
6. Deploy → **Copy the backend URL**

### 2. Connect Frontend (2 minutes)

1. Go to your **Frontend Project** in Vercel
2. Settings → Environment Variables
3. Add:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://your-backend-url.vercel.app` (from step 1)
4. Redeploy frontend

### 3. Test

1. Open your frontend: `https://the-ai-engineer-challenge-rouge-eta.vercel.app`
2. Send a message
3. Should work! ✅

## 📋 Checklist

- [ ] Backend deployed to Vercel
- [ ] `OPENAI_API_KEY` set in backend
- [ ] `FRONTEND_URL` set in backend (optional but recommended)
- [ ] `NEXT_PUBLIC_API_URL` set in frontend
- [ ] Frontend redeployed
- [ ] Tested sending a message

## 🔧 Current Configuration

**Backend (`api/index.py`):**
- ✅ CORS configured for frontend URL
- ✅ Supports environment-based CORS
- ✅ Error handling for OpenAI API

**Frontend (`frontend/services/api.ts`):**
- ✅ Uses `NEXT_PUBLIC_API_URL` environment variable
- ✅ Falls back to relative paths if not set
- ✅ Improved error handling
- ✅ Network error detection

## 🆘 Troubleshooting

**Frontend shows connection error:**
- Check `NEXT_PUBLIC_API_URL` is set in Vercel
- Verify backend URL is correct (starts with `https://`)
- Check browser console for CORS errors

**CORS errors:**
- Set `FRONTEND_URL` in backend environment variables
- Redeploy backend
- Ensure URLs match exactly

**Backend returns 500:**
- Check `OPENAI_API_KEY` is set
- View backend logs in Vercel dashboard
- Verify OpenAI API key is valid

## 📚 Full Documentation

- **Detailed Guide**: See `SECURE_DEPLOYMENT_GUIDE.md`
- **Backend Deployment**: See `BACKEND_DEPLOYMENT.md`
- **Troubleshooting**: See `TROUBLESHOOTING_BACKEND.md`

