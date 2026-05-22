# 🔥 Firebase Authentication Setup Guide

## 📋 Complete Setup Instructions

### **Step 1: Install Dependencies**

```bash
cd path_generator
pip install -r requirements.txt
```

This will install:
- Flask
- flask-cors
- pandas
- numpy
- requests
- **python-dotenv** (for environment variables)

---

### **Step 2: Configure Environment Variables**

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your Firebase credentials:
   ```env
   FIREBASE_API_KEY=your_firebase_api_key_here
   FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
   FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   FIREBASE_APP_ID=your_app_id
   FIREBASE_MEASUREMENT_ID=your_measurement_id
   ```

**✅ Replace with your actual Firebase credentials from Firebase Console!**

---

### **Step 3: Firebase Console Configuration**

#### **3.1 Enable Google Authentication**

1. Go to: **https://console.firebase.google.com/**
2. Select your project
3. Click **Authentication** in left sidebar
4. Click **Sign-in method** tab
5. Find **Google** provider
6. Click on it and toggle **Enable**
7. Select **Project support email** from dropdown
8. Click **Save**

#### **3.2 Add Authorized Domains**

1. Still in **Authentication** section
2. Click **Settings** tab
3. Scroll to **Authorized domains**
4. Verify `localhost` is in the list (it should be by default)
5. If not, click **Add domain** and add:
   - `localhost`
   - `127.0.0.1` (optional)

---

### **Step 4: Start the Server**

```bash
cd path_generator
python app.py
```

You should see:
```
🚀 AI-Powered Personalized Learning Path Generator
Server starting on http://localhost:5000
```

---

### **Step 5: Test Firebase Authentication**

1. **Open browser:** http://localhost:5000/profile.html

2. **Click:** "Sign in with Google" button

3. **Select** your Google account in the popup

4. **Success!** You should see:
   - Your profile picture
   - Your name and email
   - "Sign Out" button
   - Name field pre-filled (but editable!)

---

## 🎯 Key Features

### **1. Secure Configuration**
- ✅ Firebase credentials stored in `.env` file
- ✅ Not committed to Git (in `.gitignore`)
- ✅ Served securely via backend API endpoint

### **2. Editable Name Field**
- ✅ Name auto-filled from Google account
- ✅ User can edit/rename as needed
- ✅ Visual indicators show field is editable
- ✅ Helpful tooltip explains editability

### **3. Demo Mode**
- ✅ "Continue with Demo Gmail" button
- ✅ Bypasses authentication for testing
- ✅ Uses mock user data

---

## 🔧 How It Works

### **Backend (app.py)**
```python
@app.route('/firebase-config', methods=['GET'])
def get_firebase_config():
    """Serve Firebase config from .env"""
    firebase_config = {
        'apiKey': os.getenv('FIREBASE_API_KEY'),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
        # ... other config
    }
    return jsonify(firebase_config)
```

### **Frontend (firebase-config.js)**
```javascript
// Fetch config from backend (secure!)
const response = await fetch('/firebase-config');
const firebaseConfig = await response.json();

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
```

### **Authentication Flow**
```
User clicks "Sign in with Google"
    ↓
Firebase popup opens
    ↓
User selects Google account
    ↓
Firebase returns user data
    ↓
Store in localStorage
    ↓
Pre-fill form (name is editable!)
    ↓
User completes registration
```

---

## 📁 File Structure

```
path_generator/
├── .env                    # ⚠️ SECRET - Firebase credentials
├── .env.example            # Template for .env
├── .gitignore              # Prevents .env from being committed
├── firebase-config.js      # Fetches config from backend
├── firebase-auth.js        # Handles authentication
├── profile.html            # Profile page with auth
├── app.py                  # Flask backend with /firebase-config endpoint
└── requirements.txt        # Includes python-dotenv
```

---

## 🔒 Security Best Practices

### **✅ What We Did Right**

1. **Environment Variables**
   - Credentials in `.env` file
   - Not in source code
   - Not committed to Git

2. **Backend API**
   - Config served via `/firebase-config` endpoint
   - Validated before sending
   - Error handling included

3. **Git Protection**
   - `.env` in `.gitignore`
   - `.env.example` for reference
   - Clear documentation

### **⚠️ Important Notes**

- **Never commit `.env` file** to Git
- **Never share `.env` file** publicly
- **Use different credentials** for production
- **Rotate keys** if accidentally exposed

---

## 🐛 Troubleshooting

### **Issue: "Firebase configuration incomplete"**
**Solution:**
- Check `.env` file exists
- Verify all variables are set
- Restart Flask server

### **Issue: "This domain is not authorized"**
**Solution:**
- Go to Firebase Console → Authentication → Settings
- Add `localhost` to Authorized domains
- Wait 1-2 minutes for changes to propagate

### **Issue: "Popup blocked"**
**Solution:**
- Allow popups for `localhost:5000`
- Try in different browser
- Use "Demo Gmail" button instead

### **Issue: Name field is readonly**
**Solution:**
- It's not! The field is always editable
- Look for the blue "Editable" badge
- Click in the field and type

---

## 🎨 UI Features

### **Name Field Indicators**

When authenticated, you'll see:

1. **Blue "Editable" badge** next to "Full Name" label
2. **Help text** below field: "You can edit the name from Google authentication"
3. **Border highlight** (briefly) to draw attention
4. **Pre-filled value** from Google account

### **Authentication Status**

- **Before sign-in:** "Sign in with Google" button
- **After sign-in:** 
  - Profile picture
  - Name and email
  - "Sign Out" button

---

## 📊 API Endpoints

### **New Endpoint**
```
GET /firebase-config
```

**Response:**
```json
{
  "apiKey": "your_firebase_api_key",
  "authDomain": "your-project.firebaseapp.com",
  "projectId": "your-project-id",
  "storageBucket": "your-project.firebasestorage.app",
  "messagingSenderId": "your_sender_id",
  "appId": "your_app_id",
  "measurementId": "your_measurement_id"
}
```

---

## ✅ Testing Checklist

- [ ] `.env` file created with Firebase credentials
- [ ] `python-dotenv` installed
- [ ] Flask server running
- [ ] Google Sign-In enabled in Firebase Console
- [ ] `localhost` in Authorized domains
- [ ] Can click "Sign in with Google"
- [ ] Popup opens successfully
- [ ] Can select Google account
- [ ] Profile info displayed after sign-in
- [ ] Name field is pre-filled
- [ ] Name field is editable (can type)
- [ ] "Editable" badge visible
- [ ] Can complete registration form

---

## 🚀 Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Verify .env file exists
cat .env

# 3. Start server
python app.py

# 4. Open browser
# http://localhost:5000/profile.html

# 5. Test authentication
# Click "Sign in with Google"
```

---

## 📞 Need Help?

1. **Check browser console** (F12) for errors
2. **Check Flask terminal** for backend errors
3. **Verify Firebase Console** settings
4. **Try Demo Mode** if Firebase isn't working
5. **Check `.env` file** has all variables

---

**🎉 You're all set! Enjoy secure Firebase authentication with editable user profiles!**
