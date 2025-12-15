# 🚀 Deploying Job AI to Vercel

## ⚠️ Important: Backend Considerations

Vercel is optimized for **frontend applications**. For the backend, you have two options:

### Option 1: Hybrid Deployment (Recommended) ✅
- **Frontend**: Vercel (fast, free, optimized)
- **Backend**: Render/Railway (better for Python/FastAPI)

### Option 2: Full Vercel Deployment
- **Frontend**: Vercel
- **Backend**: Vercel Serverless Functions (has limitations)

**Limitations of Vercel for Backend:**
- 10-second timeout on free tier (job scraping may timeout)
- No persistent file storage (SQLite won't work)
- Cold starts (slower first request)
- Limited to serverless architecture

---

## 🎯 Option 1: Frontend on Vercel + Backend on Render (RECOMMENDED)

This is the best approach for your app!

### Step 1: Deploy Backend to Render

Follow the `RENDER_DEPLOYMENT_GUIDE.md` to deploy your backend to Render.

You'll get a URL like: `https://job-ai-backend.onrender.com`

### Step 2: Deploy Frontend to Vercel

#### A. Install Vercel CLI (Optional)
```bash
npm install -g vercel
```

#### B. Deploy via Vercel Dashboard (Easier)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New Project"**
3. Import your Git repository
4. Configure:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

5. **Environment Variables** (IMPORTANT):
   ```
   NEXT_PUBLIC_API_URL = https://job-ai-backend.onrender.com
   ```

6. Click **"Deploy"**

#### C. Deploy via CLI (Alternative)

```bash
cd frontend
vercel
```

Follow the prompts:
- Set up and deploy? **Y**
- Which scope? (Select your account)
- Link to existing project? **N**
- Project name? **job-ai-frontend**
- Directory? **./frontend**
- Override settings? **N**

Add environment variable:
```bash
vercel env add NEXT_PUBLIC_API_URL
# Enter: https://job-ai-backend.onrender.com
# Select: Production, Preview, Development
```

Deploy to production:
```bash
vercel --prod
```

### Step 3: Update Backend CORS

Edit `backend/main.py` to allow your Vercel domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://job-ai-frontend.vercel.app",  # Add this
        "https://your-custom-domain.com"  # If you have one
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push to redeploy backend.

### ✅ Done!

Your app is now live:
- **Frontend**: `https://job-ai-frontend.vercel.app`
- **Backend**: `https://job-ai-backend.onrender.com`

---

## 🔧 Option 2: Full Vercel Deployment (Advanced)

If you want to deploy both to Vercel, follow these steps:

### Step 1: Restructure Backend for Serverless

Create `api/index.py` in your project root:

```python
from fastapi import FastAPI
from mangum import Mangum
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

# Wrap FastAPI app with Mangum for serverless
handler = Mangum(app)
```

### Step 2: Update Requirements

Create `requirements.txt` in project root:
```
fastapi
uvicorn
mangum
requests
python-dotenv
pydantic
sqlalchemy
bcrypt>=4.0.0
python-jose[cryptography]
python-multipart
email-validator
reportlab
PyPDF2
psycopg2-binary
```

### Step 3: Create `vercel.json`

Create in project root:

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
  ],
  "env": {
    "DATABASE_URL": "@database_url",
    "SECRET_KEY": "@secret_key"
  }
}
```

### Step 4: Update Frontend API URL

In `frontend/.env.production`:
```
NEXT_PUBLIC_API_URL=/api
```

### Step 5: Deploy to Vercel

```bash
vercel
```

Add environment variables in Vercel dashboard:
- `DATABASE_URL` - PostgreSQL connection string (use Neon, Supabase, or PlanetScale)
- `SECRET_KEY` - Generate a secure key
- `GOOGLE_API_KEY` - Optional
- `GOOGLE_SEARCH_ENGINE_ID` - Optional

### ⚠️ Limitations

- **10-second timeout**: Job scraping may fail
- **No SQLite**: Must use PostgreSQL (Neon, Supabase)
- **Cold starts**: First request is slow
- **No background jobs**: Auto-apply with Selenium won't work

---

## 📊 Comparison

| Feature | Vercel Only | Vercel + Render |
|---------|-------------|-----------------|
| Setup Complexity | Medium | Easy |
| Frontend Speed | ⚡ Fast | ⚡ Fast |
| Backend Performance | 🐌 Slower (serverless) | 🚀 Fast (always-on) |
| Database | Must use PostgreSQL | SQLite or PostgreSQL |
| Timeout Limits | 10 seconds | No limit |
| Auto-Apply (Selenium) | ❌ Won't work | ✅ Works |
| Cost (Free Tier) | Free | Free |
| Recommended For | Simple APIs | Full-stack apps |

---

## 🎯 Recommended Approach

**Use Option 1: Frontend on Vercel + Backend on Render**

### Why?
- ✅ Best performance for both frontend and backend
- ✅ No timeout issues
- ✅ Auto-apply with Selenium works
- ✅ Easier to manage
- ✅ Better for long-running operations
- ✅ Can use SQLite or PostgreSQL

---

## 🚀 Quick Deploy Commands

### Frontend to Vercel:
```bash
cd frontend
vercel --prod
```

### Backend to Render:
Follow `RENDER_DEPLOYMENT_GUIDE.md`

---

## 🐛 Troubleshooting

### CORS Errors
- Add your Vercel domain to backend CORS settings
- Redeploy backend after changes

### Environment Variables Not Working
- Check Vercel dashboard → Project Settings → Environment Variables
- Redeploy after adding variables

### API Not Found (404)
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check if backend is running

### Build Fails
- Check build logs in Vercel dashboard
- Verify all dependencies in `package.json`

---

## 📞 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)

---

## ✅ Post-Deployment Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Render
- [ ] Environment variables configured
- [ ] CORS updated in backend
- [ ] Database connected (PostgreSQL)
- [ ] Test registration/login
- [ ] Test job search
- [ ] Test profile update
- [ ] Test resume generation
- [ ] Custom domain configured (optional)

---

## 🎉 You're Live!

Your Job AI app is now deployed and accessible worldwide! 🚀
