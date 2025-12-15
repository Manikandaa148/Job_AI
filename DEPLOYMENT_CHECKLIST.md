# 🚀 Quick Deployment Checklist for Render

## Before You Start
- [ ] Push your code to GitHub/GitLab/Bitbucket
- [ ] Create a Render account at https://render.com

## Backend Deployment (5-10 minutes)

### 1. Create PostgreSQL Database
- [ ] New + → PostgreSQL
- [ ] Name: `job-ai-db`
- [ ] Plan: Free
- [ ] Save the Internal Database URL

### 2. Create Backend Web Service
- [ ] New + → Web Service
- [ ] Connect your repository
- [ ] Root Directory: `backend`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 3. Environment Variables
```
SECRET_KEY = (Generate Value)
DATABASE_URL = (From PostgreSQL database - Internal URL)
GOOGLE_API_KEY = (Optional - your API key)
GOOGLE_SEARCH_ENGINE_ID = (Optional - your search engine ID)
PYTHON_VERSION = 3.11.0
```

- [ ] Click "Create Web Service"
- [ ] Wait for deployment (5-10 min)
- [ ] **Copy your backend URL**: `https://your-backend.onrender.com`

## Frontend Deployment (5-10 minutes)

### 1. Create Frontend Web Service
- [ ] New + → Web Service
- [ ] Same repository
- [ ] Root Directory: `frontend`
- [ ] Build Command: `npm install && npm run build`
- [ ] Start Command: `npm start`

### 2. Environment Variables
```
NEXT_PUBLIC_API_URL = https://your-backend.onrender.com
NODE_VERSION = 20
```

- [ ] Click "Create Web Service"
- [ ] Wait for deployment (5-10 min)
- [ ] **Your app is live!** 🎉

## Post-Deployment

### Update CORS (Important!)
- [ ] Edit `backend/main.py`
- [ ] Update CORS origins to include your frontend URL
- [ ] Commit and push (auto-redeploys)

### Test Your App
- [ ] Visit your frontend URL
- [ ] Register a new account
- [ ] Search for jobs
- [ ] Update profile
- [ ] Generate resume
- [ ] Try auto-apply

## URLs to Save
- **Frontend**: `https://job-ai-frontend.onrender.com`
- **Backend**: `https://job-ai-backend.onrender.com`
- **Backend Health**: `https://job-ai-backend.onrender.com/health`
- **API Docs**: `https://job-ai-backend.onrender.com/docs`

## ⚠️ Important Notes
- Free tier services sleep after 15 min of inactivity
- First request after sleep takes 30-60 seconds
- Upgrade to $7/month for always-on services
- Database expires after 90 days on free tier

## 🐛 Troubleshooting
- **502 Error**: Wait 30-60 seconds for service to wake up
- **CORS Error**: Check CORS settings in backend
- **Can't connect**: Verify NEXT_PUBLIC_API_URL is correct
- **Build fails**: Check logs in Render dashboard

## 📚 Full Guide
See `RENDER_DEPLOYMENT_GUIDE.md` for detailed instructions.
