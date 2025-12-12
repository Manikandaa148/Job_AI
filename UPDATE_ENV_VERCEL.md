# How to Update NEXT_PUBLIC_API_URL in Vercel

## 📍 Step-by-Step Guide

### Step 1: Get Your Backend URL from Render

After deploying your backend to Render, you'll get a URL like:
```
https://job-ai-backend-xxxx.onrender.com
```

**Copy this URL!** You'll need it in the next steps.

---

### Step 2: Go to Vercel Dashboard

1. Open: https://vercel.com/dashboard
2. Click on your **Job AI** project
3. Click the **"Settings"** tab at the top

---

### Step 3: Navigate to Environment Variables

1. In the left sidebar, click **"Environment Variables"**
2. You'll see a list of your current environment variables

---

### Step 4: Add or Update NEXT_PUBLIC_API_URL

#### If the variable doesn't exist yet:

1. Click the **"Add New"** button (top right)
2. Fill in the form:
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://your-backend-url.onrender.com
   ```
   (Replace with your actual Render URL)
3. **Select environments**: Check all three boxes:
   - ✅ Production
   - ✅ Preview
   - ✅ Development
4. Click **"Save"**

#### If the variable already exists:

1. Find **NEXT_PUBLIC_API_URL** in the list
2. Click the **"..."** menu button on the right
3. Click **"Edit"**
4. Update the **Value** to your Render URL:
   ```
   https://your-backend-url.onrender.com
   ```
5. Make sure all environments are checked:
   - ✅ Production
   - ✅ Preview
   - ✅ Development
6. Click **"Save"**

---

### Step 5: Redeploy Your Frontend

**Important:** Environment variable changes don't automatically apply to existing deployments!

1. Click the **"Deployments"** tab at the top
2. Find your latest deployment (should be at the top)
3. Click the **"..."** menu button on the right
4. Click **"Redeploy"**
5. In the popup, click **"Redeploy"** again to confirm

---

### Step 6: Wait for Deployment

You'll see:
```
⏳ Building...
⏳ Deploying...
✅ Ready
```

This usually takes 1-2 minutes.

---

### Step 7: Test Your Deployment

1. Click on the deployment URL (e.g., `your-project.vercel.app`)
2. Try to login or create an account
3. It should now work! ✅

---

## 🔍 Visual Reference

### What the Environment Variables page looks like:

```
Environment Variables
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Add New] button

Name                          Value                    Environments
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEXT_PUBLIC_API_URL          https://job-ai-ba...    Production, Preview, Development  [...]
```

### When editing:

```
Edit Environment Variable
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Name
┌─────────────────────────────────────┐
│ NEXT_PUBLIC_API_URL                 │
└─────────────────────────────────────┘

Value
┌─────────────────────────────────────┐
│ https://job-ai-backend.onrender.com │  ← Paste your Render URL here
└─────────────────────────────────────┘

Environments
☑ Production
☑ Preview
☑ Development

[Cancel]  [Save]
```

---

## 🎯 Quick Checklist

- [ ] Got backend URL from Render (e.g., `https://xxx.onrender.com`)
- [ ] Opened Vercel → Project → Settings → Environment Variables
- [ ] Added/Updated `NEXT_PUBLIC_API_URL` with Render URL
- [ ] Selected all three environments (Production, Preview, Development)
- [ ] Saved the variable
- [ ] Went to Deployments tab
- [ ] Redeployed the latest deployment
- [ ] Waited for deployment to complete
- [ ] Tested the live site - login/signup works! ✅

---

## 🆘 Troubleshooting

### "I don't see Environment Variables in the sidebar"
- Make sure you're in the **Settings** tab (top of page)
- Look for "Environment Variables" in the left sidebar
- It's usually between "Domains" and "Git"

### "My changes aren't working"
- Did you **redeploy** after changing the variable?
- Environment variables only apply to NEW deployments
- Check that you selected all three environments when saving

### "I get CORS errors"
- Make sure your backend URL doesn't have a trailing slash
- ✅ Correct: `https://backend.onrender.com`
- ❌ Wrong: `https://backend.onrender.com/`

### "API calls still go to localhost"
- Clear your browser cache
- Try in incognito/private mode
- Check browser console for the actual URL being called

---

## 📝 Example Values

Here are example values for reference:

**Development/Testing:**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Production (Render):**
```
NEXT_PUBLIC_API_URL=https://job-ai-backend-abc123.onrender.com
```

**Production (Railway):**
```
NEXT_PUBLIC_API_URL=https://job-ai-backend-production.up.railway.app
```

---

## 🎬 Summary in 3 Steps

1. **Vercel Dashboard** → Your Project → **Settings** → **Environment Variables**
2. **Edit** `NEXT_PUBLIC_API_URL` → Paste your **Render URL** → **Save**
3. **Deployments** tab → **Redeploy** latest deployment

Done! 🎉

---

Need more help? Feel free to ask!
