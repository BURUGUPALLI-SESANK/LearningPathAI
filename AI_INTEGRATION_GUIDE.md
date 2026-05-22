# 🤖 AI Integration Guide - OpenRouter + Firestore

## Overview

This system uses **OpenRouter API** with **Nvidia Nemotron model** to generate:
1. **Personalized Learning Paths** with real course URLs
2. **Study Notes** for any topic

All generated content is **cached in Firestore** to:
- ✅ Reduce API calls (save money)
- ✅ Improve response time
- ✅ Avoid rate limiting

---

## 🔑 Configuration

### Environment Variables (.env)

```env
# OpenRouter API
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free

# Firebase (for Firestore caching)
FIREBASE_PROJECT_ID=your_firebase_project_id
FIREBASE_API_KEY=your_firebase_api_key
# ... other Firebase config
```

---

## 📦 Installation

```bash
cd path_generator

# Install dependencies
pip install -r requirements.txt

# This includes:
# - firebase-admin (for Firestore)
# - python-dotenv (for .env)
# - requests (for API calls)
```

---

## 🚀 How It Works

### 1. Learning Path Generation

**Endpoint:** `POST /ai-generate-path`

**Flow:**
```
User requests learning path
    ↓
Check Firestore cache (by domain + skills + level)
    ↓
If cached → Return immediately (fast!)
    ↓
If not cached → Call OpenRouter API
    ↓
Parse AI response (JSON with courses + URLs)
    ↓
Save to Firestore
    ↓
Return to user
```

**Cache Key Format:**
```
{domain}_{experience}_{skill1}_{skill2}_{skill3}
Example: web-development_intermediate_javascript_react_nodejs
```

**API generates:**
- 4-6 courses with REAL URLs
- Study plan (week-by-week)
- Additional resources
- All skills covered

### 2. Study Notes Generation

**Endpoint:** `POST /ai-generate-notes`

**Flow:**
```
User enters topic (e.g., "React Hooks")
    ↓
Check Firestore cache (by topic + level)
    ↓
If cached → Return immediately
    ↓
If not cached → Call OpenRouter API
    ↓
Parse AI response (comprehensive notes)
    ↓
Save to Firestore
    ↓
Return to user
```

**Cache Key Format:**
```
notes_{topic}_{level}
Example: notes_react_hooks_beginner
```

**AI generates:**
- Summary
- Key concepts with examples
- Learning objectives
- Prerequisites
- Practice exercises
- Additional resources
- Pro tips

---

## 🎯 API Endpoints

### 1. Generate AI Learning Path

```http
POST /ai-generate-path
Content-Type: application/json

{
  "userId": "user_123"
}
```

**Response:**
```json
{
  "success": true,
  "from_cache": false,
  "message": "Generated with AI",
  "learningPath": {
    "courses": [
      {
        "title": "React - The Complete Guide",
        "provider": "Udemy",
        "url": "https://www.udemy.com/course/react-the-complete-guide/",
        "level": "Intermediate",
        "duration": "50 hours",
        "description": "Master React with hooks, Redux, routing",
        "skills_covered": ["React", "JavaScript", "Redux"]
      }
    ],
    "study_plan": {
      "week_1": "React fundamentals and JSX",
      "week_2": "State management and hooks",
      "week_3": "Routing and API integration",
      "week_4": "Advanced patterns and optimization"
    },
    "resources": [...]
  }
}
```

### 2. Generate AI Study Notes

```http
POST /ai-generate-notes
Content-Type: application/json

{
  "topic": "React Hooks",
  "level": "beginner"
}
```

**Response:**
```json
{
  "success": true,
  "from_cache": true,
  "message": "Loaded from cache",
  "notes": {
    "topic": "React Hooks",
    "summary": "React Hooks are functions that let you use state and other React features...",
    "key_concepts": [
      {
        "concept": "useState",
        "explanation": "Manages component state",
        "example": "const [count, setCount] = useState(0)"
      }
    ],
    "learning_objectives": [...],
    "prerequisites": [...],
    "practice_exercises": [...],
    "additional_resources": [...],
    "tips": [...]
  }
}
```

---

## 💾 Firestore Structure

### Collection: `learning_paths`

```
learning_paths/
├── web-development_intermediate_javascript_react/
│   ├── learning_path: {...}
│   ├── cached_at: "2026-05-21T20:00:00"
│   └── cache_key: "web-development_intermediate_javascript_react"
│
└── data-science_beginner_python_statistics/
    ├── learning_path: {...}
    ├── cached_at: "2026-05-21T19:30:00"
    └── cache_key: "data-science_beginner_python_statistics"
```

### Collection: `notes_{topic}_{level}`

```
learning_paths/
├── notes_react_hooks_beginner/
│   ├── notes: {...}
│   ├── cached_at: "2026-05-21T20:15:00"
│   └── cache_key: "notes_react_hooks_beginner"
│
└── notes_python_classes_intermediate/
    ├── notes: {...}
    ├── cached_at: "2026-05-21T19:45:00"
    └── cache_key: "notes_python_classes_intermediate"
```

---

## 🎨 Frontend Pages

### 1. Learning Path Page (learning-path.html)

**Add AI Generation Button:**

```javascript
async function generateWithAI() {
    const userId = document.getElementById('userId').value;
    
    const response = await fetch('/ai-generate-path', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId })
    });
    
    const data = await response.json();
    
    if (data.success) {
        displayLearningPath(data.learningPath);
        
        // Show cache status
        if (data.from_cache) {
            alert('✅ Loaded from cache (instant!)');
        } else {
            alert('🤖 Generated with AI (saved for next time)');
        }
    }
}
```

### 2. Notes Page (notes.html)

**Already created!** Access at:
```
http://localhost:5000/notes.html
```

Features:
- Enter any topic
- Select your level
- Generate comprehensive notes
- See cache status
- All notes saved for reuse

---

## 💰 Cost Optimization

### How Caching Saves Money

**Without Caching:**
- User 1 requests "React path" → API call ($)
- User 2 requests "React path" → API call ($)
- User 3 requests "React path" → API call ($)
- **Total: 3 API calls**

**With Caching:**
- User 1 requests "React path" → API call ($) → Save to Firestore
- User 2 requests "React path" → Load from Firestore (free!)
- User 3 requests "React path" → Load from Firestore (free!)
- **Total: 1 API call**

### Cache Hit Rate

Typical scenarios:
- **Popular topics** (React, Python, JavaScript): 90%+ cache hit rate
- **Unique combinations**: First request generates, rest use cache
- **Same user, different time**: Always cached

---

## 🔧 Troubleshooting

### Issue: "Firebase configuration incomplete"

**Solution:**
```bash
# Check .env file
cat .env

# Verify FIREBASE_PROJECT_ID is set
echo $FIREBASE_PROJECT_ID
```

### Issue: "OpenRouter API call failed"

**Solution:**
1. Check API key in `.env`
2. Verify internet connection
3. Check OpenRouter status: https://openrouter.ai/status
4. Try different model if current one is down

### Issue: "Failed to parse AI response"

**Solution:**
- AI sometimes returns markdown-wrapped JSON
- Code automatically handles ````json` blocks
- If still failing, check raw response in logs

### Issue: Firestore permission denied

**Solution:**
```bash
# Initialize Firebase Admin with Application Default Credentials
gcloud auth application-default login

# Or set service account key
export GOOGLE_APPLICATION_CREDENTIALS="path/to/serviceAccountKey.json"
```

---

## 📊 Monitoring

### Check Cache Performance

```python
# In Python console
from ai_generator import db

# Count cached learning paths
paths = db.collection('learning_paths').stream()
print(f"Cached paths: {len(list(paths))}")

# View specific cache
doc = db.collection('learning_paths').document('web-development_intermediate_javascript').get()
if doc.exists:
    print(doc.to_dict())
```

### API Usage Tracking

OpenRouter provides usage dashboard:
1. Go to: https://openrouter.ai/activity
2. View API calls, costs, and rate limits
3. Monitor which models are used most

---

## 🚀 Testing

### Test Learning Path Generation

```bash
# Start server
python app.py

# In another terminal
curl -X POST http://localhost:5000/ai-generate-path \
  -H "Content-Type: application/json" \
  -d '{"userId":"user_test123"}'
```

### Test Notes Generation

```bash
curl -X POST http://localhost:5000/ai-generate-notes \
  -H "Content-Type: application/json" \
  -d '{"topic":"React Hooks","level":"beginner"}'
```

### Test Cache

```bash
# First call - generates with AI
curl -X POST http://localhost:5000/ai-generate-notes \
  -H "Content-Type: application/json" \
  -d '{"topic":"Python Basics","level":"beginner"}'

# Second call - loads from cache (instant!)
curl -X POST http://localhost:5000/ai-generate-notes \
  -H "Content-Type: application/json" \
  -d '{"topic":"Python Basics","level":"beginner"}'
```

---

## ✅ Checklist

- [ ] `.env` file has OpenRouter API key
- [ ] `.env` file has Firebase project ID
- [ ] `firebase-admin` installed
- [ ] Firestore database created in Firebase Console
- [ ] Server running: `python app.py`
- [ ] Test AI generation endpoint
- [ ] Test notes generation endpoint
- [ ] Verify Firestore caching works
- [ ] Check cache hit rate

---

## 🎉 Benefits

### For Users
- ✅ **Personalized** learning paths
- ✅ **Real course URLs** (not generic)
- ✅ **Comprehensive notes** for any topic
- ✅ **Fast responses** (cached content)

### For Developers
- ✅ **Cost-effective** (caching reduces API calls)
- ✅ **Scalable** (Firestore handles millions of docs)
- ✅ **Reliable** (fallback to cache if API fails)
- ✅ **Maintainable** (clean separation of concerns)

---

**🚀 You're all set! Start generating AI-powered learning paths and notes!**
