# Production Deployment Fixes

## Issues Found & Fixed

### 1. ✅ **Localhost Fallback in Production**
**Problem:** The API service was defaulting to `http://127.0.0.1:8000` when `NEXT_PUBLIC_API_URL` wasn't set, causing production to try connecting to localhost.

**Fix:** Updated `services/api.ts` to:
- Use `NEXT_PUBLIC_API_URL` if set
- Use localhost ONLY when actually running on localhost
- Use relative paths (empty string) in production, which allows Vercel rewrites to work

### 2. ✅ **Route Not Marked as Dynamic**
**Problem:** Vercel was inferring static behavior for the route, causing caching issues.

**Fix:** Added to `app/page.tsx`:
```typescript
export const dynamic = 'force-dynamic'
export const revalidate = 0
```

### 3. ✅ **Missing Cache Control Headers**
**Problem:** No explicit cache disabling headers, leading to HTTP 304 responses.

**Fixes Applied:**
- Added cache control headers to API fetch requests in `services/api.ts`
- Added `cache: 'no-store'` option to fetch
- Added `revalidate = 0` to layout and page

### 4. ✅ **Next.js Config Localhost Fallback**
**Problem:** `next.config.js` rewrites had localhost fallback that could cause issues.

**Fix:** Updated to only use rewrites when explicitly needed or in development.

---

## Current Configuration

### Environment Variables Needed

**In Vercel Dashboard → Settings → Environment Variables:**

1. **`NEXT_PUBLIC_API_URL`** (Recommended)
   - Set to your backend API URL (e.g., `https://your-backend-api.vercel.app`)
   - If not set, the app will use relative paths and rely on `vercel.json` rewrites

### API URL Resolution Logic

The app now uses this logic to determine the API URL:

```
1. Check NEXT_PUBLIC_API_URL env var → Use it if set
2. Check if running on localhost → Use http://127.0.0.1:8000 for local dev
3. Otherwise → Use relative path '' (relies on Vercel rewrites)
```

### Vercel.json Configuration

**Important:** Update `frontend/vercel.json` with your actual backend URL:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://YOUR-ACTUAL-BACKEND-URL.vercel.app/api/:path*"
    }
  ]
}
```

Replace `YOUR-ACTUAL-BACKEND-URL` with your real backend deployment URL.

---

## Deployment Checklist

- [x] Fixed localhost fallback in `services/api.ts`
- [x] Marked page as dynamic with `export const dynamic = 'force-dynamic'`
- [x] Added cache control headers to API requests
- [x] Added `revalidate = 0` to prevent caching
- [x] Updated Next.js config to handle rewrites properly
- [ ] **TODO:** Set `NEXT_PUBLIC_API_URL` in Vercel environment variables
- [ ] **TODO:** Update `vercel.json` with actual backend URL (if using rewrites)
- [ ] **TODO:** Redeploy frontend after setting environment variables

---

## How It Works Now

### Production Flow:

1. User sends message → Frontend calls `/api/chat` (relative path)
2. Vercel rewrites (`vercel.json`) proxy to your backend
3. OR if `NEXT_PUBLIC_API_URL` is set, fetch goes directly to that URL
4. API request includes cache control headers to prevent 304 responses
5. Response is not cached

### Development Flow:

1. Detects `localhost` → Uses `http://127.0.0.1:8000`
2. Next.js rewrites handle proxying locally
3. Works seamlessly with local backend

---

## Testing

After deploying:

1. **Hard refresh** your browser (Cmd+Shift+R / Ctrl+Shift+R)
2. **Check browser console** (F12) → Network tab
3. **Send a test message**
4. **Verify:**
   - POST request to `/api/chat` (not GET)
   - Status should be 200 (not 304)
   - Request goes to correct backend URL

---

## Troubleshooting

### Still seeing HTTP 304?
- Hard refresh your browser
- Check Network tab for the actual request method (should be POST)
- Verify cache headers are being sent

### API calls failing?
- Check browser console for errors
- Verify `NEXT_PUBLIC_API_URL` is set in Vercel (or `vercel.json` has correct backend URL)
- Check Network tab to see where requests are going

### Getting localhost errors in production?
- The fix should prevent this, but verify `NEXT_PUBLIC_API_URL` is set
- Or ensure `vercel.json` rewrites are configured correctly

