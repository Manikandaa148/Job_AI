# Step-by-Step Vercel Deployment Fix

## 🎯 Follow These Exact Steps:

### Step 1: Configure Vercel Project Settings

1. **Go to your Vercel dashboard**: https://vercel.com/dashboard
2. **Click on your Job AI project**
3. **Click "Settings" tab** at the top
4. **Click "General"** in the left sidebar

5. **Scroll down to "Root Directory"**
   - Click "Edit"
   - Type: `frontend`
   - Click "Save"
   
   ⚠️ **THIS IS THE MOST IMPORTANT STEP!**

6. **Scroll down to "Build & Development Settings"**
   - Framework Preset: Should show "Next.js" (auto-detected)
   - Build Command: `npm run build` (leave as default)
   - Output Directory: `.next` (leave as default)
   - Install Command: `npm install` (leave as default)

7. **Click "Save"** if you made any changes

### Step 2: Add Environment Variable

1. **Still in Settings**, click **"Environment Variables"** in the left sidebar
2. **Click "Add New"** button
3. Fill in:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `http://localhost:8000` (temporary)
   - **Environment**: Select all (Production, Preview, Development)
4. **Click "Save"**

### Step 3: Redeploy

1. **Go to "Deployments" tab** at the top
2. **Click the "..." menu** on the latest deployment
3. **Click "Redeploy"**
4. **Click "Redeploy"** again to confirm

### Step 4: Wait for Build

The build should now succeed! ✅

You'll see:
- ✓ Building
- ✓ Deploying
- ✓ Ready

### Step 5: Test Your Deployment

1. Click on the deployment URL (e.g., `your-project.vercel.app`)
2. The frontend should load!
3. Login/signup won't work yet because backend isn't deployed

---

## 🚀 Next: Deploy Backend (Optional - for full functionality)

### Option A: Deploy Backend to Render.com (Recommended - Free)

1. **Go to**: https://render.com/
2. **Sign up/Login** with GitHub
3. **Click "New +"** → **"Web Service"**
4. **Connect your repository**: `Manikandaa148/Job_AI`
5. **Configure**:
   - Name: `job-ai-backend`
   - Root Directory: `backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. **Add Environment Variables** (click "Advanced"):
   - Copy from your `backend/.env` file
   - Add: `DATABASE_URL` if using PostgreSQL (optional)
7. **Click "Create Web Service"**
8. **Wait 5-10 minutes** for deployment

9. **Copy your backend URL** (e.g., `https://job-ai-backend.onrender.com`)

10. **Go back to Vercel**:
    - Settings → Environment Variables
    - Edit `NEXT_PUBLIC_API_URL`
    - Change value to your Render URL
    - Save and redeploy

### Option B: Use Mock Backend (Quick Test)

If you just want to test the frontend:
- The app will auto-create a guest user
- Some features won't work without real backend
- Good for UI testing

---

## ✅ Verification Checklist

- [ ] Vercel Root Directory set to `frontend`
- [ ] Environment variable `NEXT_PUBLIC_API_URL` added
- [ ] Deployment succeeded (green checkmark)
- [ ] Can access the deployed URL
- [ ] Frontend loads without errors

---

## 🆘 Troubleshooting

### Build still failing?
1. Check that Root Directory is EXACTLY `frontend` (no slash)
2. Clear build cache: Settings → General → scroll to bottom → "Clear Cache"
3. Redeploy

### "Module not found" errors?
- Root Directory is wrong - must be `frontend`

### Can't login/signup?
- Backend not deployed yet - follow Step 5 above
- Or just test the UI with guest mode

---

## 📸 Visual Guide

When setting Root Directory, you should see:
```
Root Directory: frontend
                ^^^^^^^^
                Type this exactly
```

The build output should show:
```
✓ Building
✓ Deploying  
✓ Ready
```

NOT:
```
✗ Build failed
```

---

Need help? Check the full DEPLOYMENT_GUIDE.md in your repo!
