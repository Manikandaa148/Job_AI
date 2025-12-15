# 🚀 Quick Vercel Deployment Guide

## 🎯 Choose Your Deployment Strategy

### Option A: Frontend Only on Vercel (EASIEST) ⭐ RECOMMENDED

**Best for:** Quick deployment, best performance

1. **Deploy Backend to Render** (see `RENDER_DEPLOYMENT_GUIDE.md`)
2. **Deploy Frontend to Vercel** (instructions below)

### Option B: Full Stack on Vercel (ADVANCED)

**Best for:** Everything in one place

**⚠️ Limitations:**
- 10-second timeout (job scraping may fail)
- No Selenium/browser automation
- Must use PostgreSQL (no SQLite)

---

## 📦 Option A: Frontend to Vercel (RECOMMENDED)

### Prerequisites
- Backend deployed to Render (or any hosting service)
- Backend URL (e.g., `https://job-ai-backend.onrender.com`)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Navigate to Frontend
```bash
cd frontend
```

### Step 3: Deploy
```bash
vercel
```

Answer the prompts:
- **Set up and deploy?** Y
- **Which scope?** (Select your account)
- **Link to existing project?** N
- **Project name?** job-ai-frontend
- **Directory?** ./
- **Override settings?** N

### Step 4: Add Environment Variable
```bash
vercel env add NEXT_PUBLIC_API_URL
```
Enter your backend URL: `https://job-ai-backend.onrender.com`

Select: **Production, Preview, Development** (all three)

### Step 5: Deploy to Production
```bash
vercel --prod
```

### Step 6: Update Backend CORS

Edit `backend/main.py` (around line 35):
```python
allow_origins=[
    "http://localhost:3000",
    "https://your-app.vercel.app",  # Add your Vercel URL
],
```

Commit and push to redeploy backend.

### ✅ Done!
Your app is live at: `https://your-app.vercel.app`

---

## 🔧 Option B: Full Stack on Vercel

### Prerequisites
- PostgreSQL database (Neon, Supabase, or PlanetScale)
- Vercel account

### Step 1: Install Dependencies
```bash
pip install mangum
```

### Step 2: Deploy from Root
```bash
cd "d:\Main project\Job AI_2"
vercel
```

### Step 3: Add Environment Variables in Vercel Dashboard

Go to: Project Settings → Environment Variables

Add these:
```
DATABASE_URL = postgresql://user:password@host/database
SECRET_KEY = your-secret-key-here
GOOGLE_API_KEY = your-api-key (optional)
GOOGLE_SEARCH_ENGINE_ID = your-search-id (optional)
NEXT_PUBLIC_API_URL = /api
```

### Step 4: Deploy to Production
```bash
vercel --prod
```

### ✅ Done!
- Frontend: `https://your-app.vercel.app`
- Backend API: `https://your-app.vercel.app/api`

---

## 🎨 Via Vercel Dashboard (No CLI)

### For Frontend Only:

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository
3. Configure:
   - **Framework**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
4. Add Environment Variable:
   - `NEXT_PUBLIC_API_URL` = `https://your-backend.onrender.com`
5. Click **Deploy**

### For Full Stack:

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository
3. Configure:
   - **Framework**: Next.js
   - **Root Directory**: `./` (project root)
4. Add all environment variables (see Option B, Step 3)
5. Click **Deploy**

---

## 🔍 Verify Deployment

### Check Frontend
Visit: `https://your-app.vercel.app`

### Check Backend (Full Stack Only)
Visit: `https://your-app.vercel.app/api/health`

Should return: `{"status": "ok"}`

---

## 🐛 Common Issues

### 1. "Module not found" Error
**Solution:** Ensure all dependencies are in `package.json` and `requirements.txt`

### 2. API Returns 404
**Solution:** 
- Check `NEXT_PUBLIC_API_URL` is set correctly
- For full stack: Verify `vercel.json` routes are correct

### 3. CORS Error
**Solution:** Add your Vercel domain to backend CORS settings

### 4. Database Connection Error
**Solution:** 
- Verify `DATABASE_URL` is correct
- Use PostgreSQL (not SQLite) for Vercel deployment

### 5. Build Timeout
**Solution:** 
- Reduce dependencies
- Use Vercel Pro for longer build times

---

## 📊 Deployment Comparison

| Aspect | Frontend Only | Full Stack |
|--------|---------------|------------|
| Setup Time | 5 minutes | 15 minutes |
| Complexity | Easy | Medium |
| Performance | ⚡ Excellent | 🐌 Slower |
| Limitations | None | 10s timeout |
| Selenium Support | ✅ (via Render) | ❌ |
| Database | Any | PostgreSQL only |
| **Recommended** | ✅ YES | ⚠️ Advanced users |

---

## 🎯 Recommended Steps

1. ✅ Deploy backend to Render (see `RENDER_DEPLOYMENT_GUIDE.md`)
2. ✅ Deploy frontend to Vercel (Option A above)
3. ✅ Update CORS in backend
4. ✅ Test your app
5. ✅ Add custom domain (optional)

---

## 📞 Need Help?

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Support](https://vercel.com/support)
- Check deployment logs in Vercel dashboard

---

## 🎉 Next Steps

After deployment:
- [ ] Test all features
- [ ] Set up custom domain
- [ ] Configure analytics
- [ ] Set up monitoring
- [ ] Share your app! 🚀
