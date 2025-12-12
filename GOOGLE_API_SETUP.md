# Google API Setup Guide - Fix "Google API Key or Search Engine ID not found" Warning

## 🔍 **What's the Warning?**

```
Warning: Google API Key or Search Engine ID not found.
```

This warning appears because the Google Custom Search API credentials are not configured. The app still works (it uses mock/fallback data), but to get **real job search results**, you need to set up Google API.

---

## ✅ **Option 1: Quick Fix - Use Mock Data (Already Working)**

**Good News**: Your app already works! It's using mock/fallback data when Google API is not configured.

**What you get**:
- ✅ App works fine
- ✅ Shows sample job listings
- ✅ All features work (login, profile, resume, etc.)
- ⚠️ Job search results are mock data (not real jobs)

**No action needed** if you're okay with mock data for now!

---

## 🚀 **Option 2: Set Up Google API (Real Job Search)**

If you want **real job search results**, follow these steps:

### **Step 1: Get Google API Key**

1. Go to: **https://console.cloud.google.com/**
2. Create a new project or select existing one
3. Click **"APIs & Services"** → **"Credentials"**
4. Click **"Create Credentials"** → **"API Key"**
5. **Copy the API Key** (e.g., `AIzaSyC...`)
6. Click **"Restrict Key"** (recommended):
   - API restrictions → Select **"Custom Search API"**
   - Save

### **Step 2: Enable Custom Search API**

1. Go to: **https://console.cloud.google.com/apis/library**
2. Search for **"Custom Search API"**
3. Click on it
4. Click **"Enable"**

### **Step 3: Create Custom Search Engine**

1. Go to: **https://programmablesearchengine.google.com/**
2. Click **"Add"** or **"Get Started"**
3. Fill in:
   - **Search engine name**: Job AI Search
   - **What to search**: Search the entire web
   - **Search settings**: Enable "Search the entire web"
4. Click **"Create"**
5. Click **"Customize"** → **"Setup"**
6. **Copy the Search Engine ID** (e.g., `a1b2c3d4e5f6g7h8i`)

### **Step 4: Add to Your .env File**

1. Open (or create): `d:\Main project\Job AI_2\backend\.env`
2. Add these lines:

```env
GOOGLE_API_KEY=AIzaSyC_your_actual_api_key_here
SEARCH_ENGINE_ID=a1b2c3d4e5f6g7h8i_your_actual_id_here
```

3. **Save the file**

### **Step 5: Restart Backend**

```bash
# Stop the current server (Ctrl+C)
# Then restart:
cd backend
.\venv\Scripts\uvicorn main:app --reload
```

### **Step 6: Test**

1. Go to your website
2. Search for jobs
3. You should now see **real job listings** from Google! ✅

---

## 📝 **Environment Variables Template**

I've created **`backend/.env.example`** for you. Copy it to create your `.env`:

```bash
cd backend
copy .env.example .env
```

Then edit `.env` and add your actual API keys.

---

## 🆓 **Is It Free?**

### **Google Custom Search API Pricing:**

- **Free tier**: 100 searches per day
- **Paid**: $5 per 1,000 queries (after free tier)

**For development/testing**: Free tier is usually enough!

---

## 🔧 **For Render Deployment:**

After setting up locally, add these to Render:

1. Go to: **https://dashboard.render.com/**
2. Click your backend service
3. Go to **"Environment"** tab
4. Add:
   - `GOOGLE_API_KEY` = your API key
   - `SEARCH_ENGINE_ID` = your search engine ID
5. Save
6. Service will auto-redeploy

---

## ⚠️ **Troubleshooting:**

### **"API key not valid"**
- Make sure you enabled Custom Search API
- Check API key restrictions
- Try creating a new API key

### **"Search engine ID not found"**
- Make sure you created a Programmable Search Engine
- Copy the ID from the "Setup" tab
- ID should be alphanumeric (no spaces)

### **Still seeing mock data**
- Check `.env` file exists in `backend/` folder
- Check no typos in variable names
- Restart the backend server
- Check console for error messages

---

## 🎯 **What You Get With Google API:**

| Feature | Without API (Mock Data) | With API (Real Data) |
|---------|-------------------------|----------------------|
| Job Search | ✅ Works (mock jobs) | ✅ Real job listings |
| Filters | ✅ Works | ✅ Better results |
| Location | ✅ Works | ✅ Accurate locations |
| Companies | ✅ Mock companies | ✅ Real companies |
| Job URLs | ❌ Example links | ✅ Real job links |

---

## 📊 **Current Status:**

- ✅ App is working (using mock data)
- ⚠️ Google API not configured (warning shown)
- ✅ All other features work fine
- 📝 `.env.example` template created

---

## 🎯 **Recommendation:**

### **For Development:**
- ✅ Keep using mock data (it's fine!)
- ✅ Focus on other features first
- ⏳ Add Google API later when needed

### **For Production:**
- ✅ Set up Google API
- ✅ Get real job listings
- ✅ Better user experience

---

## 📖 **Quick Start (TL;DR):**

```bash
# 1. Get API Key from Google Cloud Console
# 2. Create Search Engine at programmablesearchengine.google.com
# 3. Create .env file:
cd backend
copy .env.example .env

# 4. Edit .env and add:
GOOGLE_API_KEY=your_key_here
SEARCH_ENGINE_ID=your_id_here

# 5. Restart server
.\venv\Scripts\uvicorn main:app --reload
```

---

## ✅ **Summary:**

- ⚠️ **Warning**: Not an error, just a notice
- ✅ **App works**: Using mock data as fallback
- 🔧 **Optional**: Set up Google API for real jobs
- 📝 **Template**: `.env.example` created for you
- 🆓 **Free**: 100 searches/day on Google

---

**Your app is working fine! The warning is just informational. Set up Google API only if you want real job search results.** 👍
