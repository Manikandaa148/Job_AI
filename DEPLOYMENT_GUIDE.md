# Job AI - Vercel Deployment Guide

## Important: Vercel Configuration

This project is configured to deploy **only the frontend** to Vercel. The backend needs to be deployed separately.

### Frontend Deployment (Vercel)

1. **In Vercel Dashboard:**
   - Go to Project Settings → General
   - Set **Root Directory** to: `frontend`
   - Set **Framework Preset** to: `Next.js`
   - Build Command: `npm run build` (default)
   - Output Directory: `.next` (default)
   - Install Command: `npm install` (default)

2. **Environment Variables:**
   Add the following environment variable in Vercel:
   - `NEXT_PUBLIC_API_URL` = Your backend URL (e.g., `https://your-backend.onrender.com`)

### Backend Deployment Options

Deploy your FastAPI backend to one of these platforms:

#### Option 1: Render.com (Recommended - Free Tier Available)
1. Create a new Web Service
2. Connect your GitHub repo
3. Set Root Directory: `backend`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables from `backend/.env`

#### Option 2: Railway.app
1. Create new project from GitHub
2. Set Root Directory: `backend`
3. Add environment variables
4. Railway will auto-detect Python and deploy

#### Option 3: Vercel Serverless (Requires modification)
- Convert FastAPI to serverless functions
- Not recommended for this project structure

### After Backend Deployment

1. Copy your backend URL
2. Go to Vercel → Your Project → Settings → Environment Variables
3. Add: `NEXT_PUBLIC_API_URL` = `https://your-backend-url.com`
4. Redeploy the frontend

### Local Development

```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

Backend runs on: http://localhost:8000
Frontend runs on: http://localhost:3000

## Troubleshooting

### "Module not found" errors on Vercel
- Make sure Root Directory is set to `frontend` in Vercel settings
- Clear build cache and redeploy

### API calls failing
- Check that `NEXT_PUBLIC_API_URL` environment variable is set correctly in Vercel
- Ensure backend is deployed and accessible
- Check CORS settings in `backend/main.py`

### Database errors
- Make sure to set up a production database (not SQLite)
- Update database connection in backend environment variables
