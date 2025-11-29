# Vercel Configuration Guide

## Backend API URL Configuration

The frontend can connect to the backend in two ways:

### Option 1: Environment Variable (Recommended)

Set the `NEXT_PUBLIC_API_URL` environment variable in Vercel:

1. Go to your Vercel project → Settings → Environment Variables
2. Add: `NEXT_PUBLIC_API_URL` = `https://your-backend-url.vercel.app`
   - Or use your custom backend URL: `http://YOUR_IP_ADDRESS:8000`
3. Redeploy your frontend

**This takes precedence over `vercel.json` rewrites.**

### Option 2: Update vercel.json

If you don't set `NEXT_PUBLIC_API_URL`, the frontend will use Vercel rewrites from `vercel.json`:

1. Update `frontend/vercel.json`
2. Replace `https://your-backend-url.vercel.app` with your actual backend URL
3. Commit and push (Vercel will auto-redeploy)

**Note:** Vercel doesn't support environment variables directly in `vercel.json`, so you'll need to update it manually or use Option 1.

## Example URLs

- **Vercel Backend**: `https://your-backend-project.vercel.app`
- **Custom Backend**: `http://YOUR_IP_ADDRESS:8000`
- **Local Development**: `http://127.0.0.1:8000` (handled automatically)

