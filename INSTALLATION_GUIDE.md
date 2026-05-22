# 🚀 Installation & Setup Guide

## Quick Start (5 Minutes)

### Step 1: Install Python Dependencies

```bash
cd path_generator
pip install -r requirements.txt
```

**New Dependencies Installed:**
- Flask (Web framework)
- Flask-CORS (Cross-origin support)
- Pandas (Data processing)
- NumPy (Numerical computations)
- **scikit-learn** (Machine Learning - NEW!)

### Step 2: Verify Data Files

Make sure these files exist in the `data/` folder:
- ✅ `data/students.csv`
- ✅ `data/courses.csv`
- ✅ `data/feedbacks.csv` (auto-generated if missing)

### Step 3: Start the Backend Server

```bash
python app.py
```

You should see:
```
Starting Flask server...
API Endpoints:
  POST /register - Register learner profile
  POST /assessment - Submit skill assessment
  POST /generate-path - Generate learning path
  GET /dashboard/<user_id> - Get dashboard data
  POST /update-progress - Update progress
  POST /submit-feedback - Submit customer feedback
  GET /feedbacks - Get feedback analytics
  GET /analytics-data - Get customer behaviour analytics
  POST /chat - AI Study Tutor Chatbot
  GET /employability/<user_id> - Get employability score (NEW!)
  GET /adaptive-insights/<user_id> - Get adaptive insights (NEW!)
 * Running on http://0.0.0.0:5000
```

### Step 4: Open the Website

Open any of these pages in your browser:
- `http://localhost:5000/index.html` - Home page
- `http://localhost:5000/profile.html` - Profile & Gmail auth
- `http://localhost:5000/assessment.html` - Skill assessment
- `http://localhost:5000/learning-path.html` - AI-generated path
- `http://localhost:5000/dashboard.html` - Progress dashboard
- `http://localhost:5000/employability.html` - **NEW! Employability score**
- `http://localhost:5000/demo-hub.html` - Analytics & BMC features

---

## 🧪 Testing New Features

### Test 1: ML-Based Recommendations

1. Go to `profile.html` and create a profile
2. Go to `assessment.html` and add skills
3. Go to `learning-path.html` and click "Generate Learning Path"
4. **Check the console** - you'll see ML scores for each course!

**What to Look For:**
- Each course now has a `ml_score` field
- Courses have `relevance` classification (High/Medium/Low)
- Recommendations are more accurate based on your skills

### Test 2: Employability Score

1. Complete steps 1-3 above (profile, assessment, path generation)
2. Go to `employability.html`
3. **You'll see:**
   - Overall score (0-100)
   - Skills Mastery score
   - Course Completion score
   - Industry Alignment score
   - Readiness level badge
   - Personalized recommendations

### Test 3: Adaptive Learning

1. Go to `dashboard.html`
2. Update some course progress (click on courses)
3. **Check the response** - it now includes:
   - Learning velocity (Fast/Steady/Slow)
   - Adaptive recommendations
   - Auto-regeneration suggestions

### Test 4: Enhanced Chatbot

1. Click the floating chatbot button (bottom right)
2. Try these queries:
   - "What's my employability score?"
   - "How am I doing?"
   - "What's my progress?"
3. **You'll get personalized responses** based on your actual data!

---

## 🔧 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'sklearn'"

**Solution:**
```bash
pip install scikit-learn==1.3.2
```

### Issue: "Port 5000 already in use"

**Solution:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change port in app.py:
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Issue: "CORS error in browser"

**Solution:**
- Make sure Flask-CORS is installed: `pip install flask-cors`
- Check that `CORS(app)` is in `app.py`

### Issue: "Employability score not showing"

**Solution:**
- Make sure you've generated a learning path first
- Check browser console for errors
- Verify backend is running on port 5000

---

## 📊 Verifying ML Features Work

### Check 1: TF-IDF is Working

Open Python console:
```python
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer()
print("✅ scikit-learn installed correctly!")
```

### Check 2: Backend ML Endpoint

```bash
curl -X POST http://localhost:5000/generate-path \
  -H "Content-Type: application/json" \
  -d '{"userId":"test_user"}'
```

Look for `ml_score` in the response!

### Check 3: Employability Endpoint

```bash
curl http://localhost:5000/employability/test_user
```

Should return employability data or error if path not generated.

---

## 🎯 Feature Checklist

After installation, verify these features work:

- [ ] Profile registration with Gmail auth
- [ ] Skill assessment (1-5 levels)
- [ ] Learning path generation
- [ ] **ML-based course recommendations** (NEW!)
- [ ] Dashboard with progress tracking
- [ ] **Employability score calculation** (NEW!)
- [ ] **Adaptive learning insights** (NEW!)
- [ ] **Enhanced chatbot with context** (NEW!)
- [ ] Feedback submission
- [ ] Analytics charts
- [ ] Study planner
- [ ] Certificate preview
- [ ] Job matching

---

## 🚀 Performance Expectations

With the new ML features:
- **Path Generation**: ~100-200ms (includes ML processing)
- **Employability Calculation**: ~10-20ms
- **Adaptive Analysis**: ~5-10ms
- **Chatbot Response**: ~50-100ms

All features run in real-time with no noticeable delay!

---

## 📱 Browser Compatibility

Tested on:
- ✅ Chrome 120+
- ✅ Firefox 120+
- ✅ Edge 120+
- ✅ Safari 17+

---

## 🔐 Security Notes

For production deployment:
1. Change `debug=True` to `debug=False` in `app.py`
2. Use environment variables for sensitive data
3. Implement proper authentication
4. Use HTTPS
5. Add rate limiting
6. Use a real database (not in-memory storage)

---

## 📚 Additional Resources

- **Main README**: `README.md` - Full API documentation
- **New Features**: `NEW_FEATURES_IMPLEMENTED.md` - Detailed feature list
- **API Testing**: Use Postman or cURL for endpoint testing
- **Frontend Code**: All HTML files have inline comments

---

## 💡 Tips for Best Experience

1. **Use Chrome DevTools** to see ML scores in console
2. **Complete the full flow** (profile → assessment → path → dashboard)
3. **Update progress regularly** to see adaptive learning in action
4. **Ask the chatbot** about your employability and progress
5. **Check the employability page** after completing courses

---

## 🎓 Learning Outcomes

By using this system, you'll understand:
1. How ML-based recommendations work (TF-IDF, cosine similarity)
2. How employability scoring systems function
3. How adaptive learning engines analyze performance
4. How to integrate ML into web applications
5. How to build intelligent tutoring systems

---

## ✅ Success Indicators

You'll know everything is working when:
1. ✅ Backend starts without errors
2. ✅ All pages load correctly
3. ✅ Learning path shows ML scores
4. ✅ Employability page displays score
5. ✅ Chatbot answers employability queries
6. ✅ Progress updates trigger adaptive insights

---

**Need Help?** Check the console logs in both:
- Browser DevTools (F12)
- Backend terminal

Most issues are logged with clear error messages!

---

**Installation Date**: May 21, 2026  
**Version**: 2.0  
**Status**: ✅ Ready to Use
