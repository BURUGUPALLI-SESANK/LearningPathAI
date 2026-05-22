# 🚀 Vercel Deployment Guide

## Quick Start

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Ready for Vercel"
git remote add origin YOUR_GITHUB_URL
git push -u origin main
```

### 2. Deploy on Vercel
1. Go to https://vercel.com
2. Click "Add New Project"
3. Import your GitHub repository
4. Add environment variables (see below)
5. Click "Deploy"

### 3. Environment Variables
Add these in Vercel dashboard:
- `OPENROUTER_API_KEY` = your_api_key
- `FIREBASE_PROJECT_ID` = your_project_id
- `FIREBASE_API_KEY` = your_firebase_key

### 4. Update API URLs
After deployment, replace in ALL HTML files:
```javascript
const API_BASE = 'http://localhost:5000';
```
With:
```javascript
const API_BASE = 'https://YOUR-PROJECT.vercel.app/api';
```

## Files Created
- ✅ `vercel.json` - Configuration
- ✅ `api/index.py` - Serverless function
- ✅ `.vercelignore` - Ignore file

## Done!
Your app will be live at: `https://YOUR-PROJECT.vercel.app`

🚀 **Ready to deploy!**
