# 🔐 Authentication System Guide

## Overview
The Job AI platform now has a **mandatory authentication system** that ensures only authorized users can access the application. Users must login before using any features.

---

## 🎯 Key Features

### 1. **Mandatory Login**
- Users **must login** when they first visit the website
- No access to job search or auto-apply without authentication
- Automatic redirect to login page if not authenticated

### 2. **Remember Me**
- ✅ **Checkbox** on login page
- Saves your email and password securely in browser
- **Auto-fills credentials** on next visit
- One-click login for returning users

### 3. **Automatic Redirect**
- Not logged in? → Redirected to `/login`
- Logged in? → Access to all features
- After login → Redirected to home page

---

## 🚀 How It Works

### **First Time Visit**
```
User opens website
    ↓
AuthWrapper checks for token
    ↓
No token found
    ↓
Redirect to /login page
    ↓
User enters credentials
    ↓
[✓] Remember Me (optional)
    ↓
Login successful
    ↓
Token saved to localStorage
    ↓
Redirect to home page
    ↓
Access granted! 🎉
```

### **Returning User (with Remember Me)**
```
User opens website
    ↓
AuthWrapper checks for token
    ↓
No token → Redirect to /login
    ↓
Login page loads
    ↓
Email & Password auto-filled! ✨
    ↓
User clicks "Sign In"
    ↓
Instant access! 🚀
```

### **Returning User (without Remember Me)**
```
User opens website
    ↓
AuthWrapper checks for token
    ↓
No token → Redirect to /login
    ↓
User enters credentials manually
    ↓
Login successful
    ↓
Access granted!
```

---

## 📋 Login Page Features

### **Login Mode**
- Email address field
- Password field (with show/hide toggle)
- **Remember Me checkbox** ✓
- Sign In button
- Link to switch to registration

### **Registration Mode**
- Full name field
- Email address field
- Password field (with show/hide toggle)
- Create Account button
- Link to switch to login

### **Remember Me Checkbox**
- **Only visible in Login mode**
- Saves credentials to browser's localStorage
- Auto-fills on next visit
- Can be unchecked to clear saved credentials

---

## 🔒 Security Features

### **Token-Based Authentication**
- JWT tokens for secure authentication
- Stored in localStorage
- Sent with every API request
- Validated by backend

### **Password Security**
- Passwords hashed on backend
- Never stored in plain text
- Show/hide password toggle for convenience

### **Remember Me Security**
- Credentials stored in browser only
- Not sent to server
- Cleared when unchecked
- User has full control

---

## 💡 User Experience

### **For New Users**
1. Visit website
2. See login page immediately
3. Click "Sign up"
4. Enter details and register
5. Auto-login after registration
6. Start using the platform!

### **For Returning Users**
1. Visit website
2. See login page
3. Credentials already filled (if Remember Me was checked)
4. Click "Sign In"
5. Instant access!

### **For Users Who Logout**
1. Click logout (user icon → Logout)
2. Token cleared
3. Redirected to login page
4. Must login again to access

---

## 🎨 Visual Design

### **Login Page**
- **Modern gradient background**
- **Centered card layout**
- **Blue accent colors**
- **Smooth animations**
- **Dark mode support**

### **Remember Me Checkbox**
- **Custom styled checkbox**
- **Blue when checked**
- **Smooth transitions**
- **Hover effects**

### **Loading State**
- **Spinner animation** while checking auth
- **"Loading..." message**
- **Prevents flash of wrong content**

---

## 🛠️ Technical Implementation

### **Components Created**

#### 1. **AuthWrapper** (`AuthWrapper.tsx`)
```tsx
- Wraps entire application
- Checks authentication on every page
- Redirects to /login if not authenticated
- Shows loading state during check
- Allows /login page without auth
```

#### 2. **Updated Login Page** (`login/page.tsx`)
```tsx
- Added rememberMe state
- useEffect to load saved credentials
- Save/clear credentials on login
- Auto-fill email and password
- Custom checkbox component
```

#### 3. **Updated Layout** (`layout.tsx`)
```tsx
- Wraps children with AuthWrapper
- Updated metadata
- Enforces auth on all pages
```

---

## 📊 Data Flow

### **Login Flow**
```
1. User enters credentials
2. Click "Sign In"
3. API call to /login endpoint
4. Backend validates credentials
5. Returns JWT token
6. Token saved to localStorage
7. If Remember Me checked:
   - Save email to localStorage
   - Save password to localStorage
8. Redirect to home page
```

### **Remember Me Flow**
```
1. Login page loads
2. useEffect runs
3. Check localStorage for:
   - rememberedEmail
   - rememberedPassword
4. If found:
   - Auto-fill email field
   - Auto-fill password field
   - Check Remember Me checkbox
5. User can login with one click!
```

### **Authentication Check Flow**
```
1. User navigates to any page
2. AuthWrapper checks localStorage for token
3. If token exists:
   - Allow access
   - Show page content
4. If no token:
   - Redirect to /login
   - Show login page
```

---

## 🎯 localStorage Keys

| Key | Purpose | When Saved | When Cleared |
|-----|---------|------------|--------------|
| `token` | JWT authentication token | On login | On logout |
| `rememberedEmail` | Saved email for Remember Me | On login (if checked) | On login (if unchecked) |
| `rememberedPassword` | Saved password for Remember Me | On login (if checked) | On login (if unchecked) |

---

## 🔄 User States

### **Authenticated**
- ✅ Has valid token in localStorage
- ✅ Can access all pages
- ✅ Can use auto-apply
- ✅ Can chat with bot
- ✅ Can search jobs

### **Not Authenticated**
- ❌ No token in localStorage
- ❌ Redirected to /login
- ❌ Cannot access main pages
- ❌ Must login first

### **Remembered**
- ✅ Has saved credentials
- ✅ Auto-filled on login page
- ✅ One-click login
- ✅ Better UX for returning users

---

## 🚀 Testing Guide

### **Test 1: First Time User**
1. Clear localStorage (F12 → Application → Clear)
2. Visit http://localhost:3000
3. ✅ Should redirect to /login
4. Register new account
5. ✅ Should auto-login and redirect to home

### **Test 2: Remember Me**
1. Login with Remember Me checked
2. Close browser
3. Reopen and visit http://localhost:3000
4. ✅ Should redirect to /login
5. ✅ Email and password should be filled
6. Click Sign In
7. ✅ Should login successfully

### **Test 3: Without Remember Me**
1. Login without checking Remember Me
2. Close browser
3. Reopen and visit http://localhost:3000
4. ✅ Should redirect to /login
5. ✅ Fields should be empty
6. Must enter credentials manually

### **Test 4: Logout**
1. Login successfully
2. Click user icon → Logout
3. ✅ Should clear token
4. ✅ Should redirect to /login
5. ✅ Cannot access home without login

---

## 💡 Tips for Users

1. **Check "Remember Me"** for faster login next time
2. **Use a strong password** for security
3. **Don't share credentials** with others
4. **Logout on shared computers** for security
5. **Uncheck Remember Me** on public computers

---

## 🎉 Benefits

### **For Users**
- ✅ Secure access to platform
- ✅ Personalized experience
- ✅ Saved preferences and data
- ✅ Quick login with Remember Me
- ✅ Professional authentication flow

### **For Platform**
- ✅ User data protection
- ✅ Authorized access only
- ✅ Better user tracking
- ✅ Improved security
- ✅ Professional appearance

---

## 🔧 Troubleshooting

### **Can't access home page**
**Solution:** Make sure you're logged in. Check if you see the login page.

### **Remember Me not working**
**Solution:** 
- Make sure you checked the box before login
- Check if localStorage is enabled in browser
- Try clearing cache and logging in again

### **Stuck on loading screen**
**Solution:**
- Refresh the page
- Clear localStorage
- Check if backend is running

### **Redirected to login after successful login**
**Solution:**
- Check browser console for errors
- Verify token is saved in localStorage
- Try logging in again

---

## 📱 Browser Compatibility

✅ **Supported Browsers:**
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Opera (latest)

⚠️ **Requirements:**
- JavaScript enabled
- localStorage enabled
- Cookies enabled

---

**Enjoy secure access to Job AI! 🔐**
