# 🚀 Deploying Job AI to Render

This guide will walk you through deploying both the **backend (FastAPI)** and **frontend (Next.js)** to Render.

## 📋 Prerequisites

1. A [Render account](https://render.com/) (free tier available)
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)
3. Environment variables ready (see below)

---

## 🔧 Part 1: Deploy Backend (FastAPI)

### Step 1: Create a PostgreSQL Database (Optional but Recommended)

1. Go to your [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `job-ai-db`
   - **Database**: `job_ai`
   - **User**: (auto-generated)
   - **Region**: Choose closest to you
   - **Plan**: **Free**
4. Click **"Create Database"**
5. **Save the connection details** (you'll need the Internal Database URL)

### Step 2: Deploy Backend Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your Git repository
3. Configure the service:
   - **Name**: `job-ai-backend`
   - **Region**: Same as your database
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `backend`
   - **Runtime**: **Python 3**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: **Free**

### Step 3: Configure Backend Environment Variables

In the **Environment** section, add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `SECRET_KEY` | Click "Generate Value" | JWT secret key |
| `DATABASE_URL` | (From PostgreSQL database) | Internal Database URL |
| `GOOGLE_API_KEY` | Your Google API key | Optional - for enhanced job search |
| `GOOGLE_SEARCH_ENGINE_ID` | Your Search Engine ID | Optional - for enhanced job search |
| `PYTHON_VERSION` | `3.11.0` | Python version |

4. Click **"Create Web Service"**

### Step 4: Wait for Deployment

- Render will build and deploy your backend
- This takes 5-10 minutes for the first deployment
- Once complete, you'll get a URL like: `https://job-ai-backend.onrender.com`
- **Save this URL** - you'll need it for the frontend!

### Step 5: Test Backend

Visit: `https://your-backend-url.onrender.com/health`

You should see: `{"status": "ok"}`

---

## 🎨 Part 2: Deploy Frontend (Next.js)

### Step 1: Update Frontend Environment Variable

Before deploying, you need to tell your frontend where the backend is:

1. In your local project, create a file: `frontend/.env.production`
2. Add this line (replace with your actual backend URL):
   ```
   NEXT_PUBLIC_API_URL=https://job-ai-backend.onrender.com
   ```

3. **Commit and push this file** to your repository:
   ```bash
   git add frontend/.env.production
   git commit -m "Add production environment variables"
   git push
   ```

### Step 2: Deploy Frontend Web Service

1. Go back to Render Dashboard
2. Click **"New +"** → **"Web Service"**
3. Connect the same Git repository
4. Configure:
   - **Name**: `job-ai-frontend`
   - **Region**: Same as backend
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Runtime**: **Node**
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`
   - **Plan**: **Free**

### Step 3: Configure Frontend Environment Variables

In the **Environment** section, add:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://job-ai-backend.onrender.com` |
| `NODE_VERSION` | `20` |

4. Click **"Create Web Service"**

### Step 4: Wait for Deployment

- Frontend deployment takes 5-10 minutes
- You'll get a URL like: `https://job-ai-frontend.onrender.com`

---

## 🔄 Part 3: Update CORS Settings

Your backend needs to allow requests from your frontend domain.

### Option 1: Update in Code (Recommended)

1. Edit `backend/main.py`
2. Find the CORS middleware section (around line 33):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://job-ai-frontend.onrender.com"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. Commit and push:
```bash
git add backend/main.py
git commit -m "Update CORS for production"
git push
```

Render will automatically redeploy your backend!

### Option 2: Use Environment Variable

Keep `allow_origins=["*"]` for simplicity (less secure but easier for testing)

---

## ✅ Part 4: Verify Everything Works

1. **Visit your frontend**: `https://job-ai-frontend.onrender.com`
2. **Test the features**:
   - Search for jobs
   - Register/Login
   - Update profile
   - Generate resume
   - Try auto-apply

---

## 🎯 Important Notes

### Free Tier Limitations

- **Backend & Frontend**: Services spin down after 15 minutes of inactivity
- **First request after inactivity**: Takes 30-60 seconds to wake up
- **Database**: 90-day expiration on free tier
- **Solution**: Upgrade to paid plan ($7/month per service) for always-on

### Database Migration

If you're using SQLite locally, you'll need to migrate to PostgreSQL for production:

1. Your backend already supports PostgreSQL via `DATABASE_URL`
2. The database tables will be created automatically on first run
3. You'll need to re-register users (local data won't transfer)

### Custom Domain (Optional)

1. Go to your frontend service settings
2. Click **"Custom Domains"**
3. Add your domain and follow DNS instructions

---

## 🐛 Troubleshooting

### Backend won't start
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure `requirements.txt` has all dependencies

### Frontend can't connect to backend
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings in backend
- Look at browser console for errors

### Database connection errors
- Verify `DATABASE_URL` is set correctly
- Check if database is in same region as backend
- Ensure database is running (not paused)

### 502 Bad Gateway
- Service is probably starting up (wait 30-60 seconds)
- Check if build succeeded in logs

---

## 📊 Monitoring

- **Logs**: Available in each service's dashboard
- **Metrics**: CPU, Memory usage visible in dashboard
- **Health Checks**: Backend has `/health` endpoint

---

## 🔐 Security Checklist

- [ ] Change `SECRET_KEY` from default
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set specific CORS origins (not `*`)
- [ ] Add rate limiting (future enhancement)
- [ ] Enable HTTPS (automatic on Render)
- [ ] Don't commit `.env` files with secrets

---

## 🎉 You're Done!

Your Job AI application is now live on Render!

**Frontend**: `https://job-ai-frontend.onrender.com`
**Backend**: `https://job-ai-backend.onrender.com`

Share your app with others and start applying to jobs! 🚀

---

## 📞 Need Help?

- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com/)
- Check the logs in your Render dashboard
