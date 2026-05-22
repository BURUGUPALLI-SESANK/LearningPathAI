# Testing Guide - AI Learning Path Generation Fix

## Quick Test Steps

### 1. Server Status ✅
The server is already running on `http://localhost:5000`

### 2. Test the Fixed Flow

#### Step 1: Open Profile Page
```
http://localhost:5000/profile.html
```
- Sign in with Firebase authentication
- Fill in your profile details
- Submit the form

#### Step 2: Open Assessment Page
```
http://localhost:5000/assessment.html
```
- Add at least 3 skills (e.g., Python, JavaScript, Data Analysis)
- Set skill levels (1-5)
- Click "Proceed to Generate Learning Path"

#### Step 3: Watch the Magic Happen ✨
The button will show progress:
1. "Submitting Assessment..." (saving to database)
2. "Generating AI Learning Path..." (calling OpenRouter API)
3. Redirect to learning-path.html with results

### 3. What to Expect

#### Success Scenario (AI Works):
- ✅ Learning path generated with real course URLs
- ✅ Courses from Coursera, Udemy, freeCodeCamp, etc.
- ✅ 4-week study plan
- ✅ Additional resources
- ✅ Alert: "🤖 AI has generated your personalized learning path!"

#### Fallback Scenario (AI Parsing Fails):
- ✅ Learning path still generated (fallback structure)
- ✅ Basic course recommendations
- ✅ Generic study plan
- ✅ System continues to work (no errors!)
- ⚠️ Server logs show "Using fallback learning path"

### 4. Check Server Logs

Watch the terminal for detailed logs:
```
🚀 AI Generate Path request for user: [user_id]
📊 Profile domain: web-development
📊 Skills count: 3
📊 Skill gaps identified: 5
🤖 Calling OpenRouter API with model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
✅ API call successful
📝 Response preview: {...}
🔍 Cleaned response preview: {...}
✅ Learning path saved successfully for user [user_id]
```

### 5. Verify Caching

Try the same flow again with the same skills:
- Should see: "✅ Cache HIT" in server logs
- Response should be instant (no API call)
- Alert: "✅ Learning path loaded from cache"

## Common Issues & Solutions

### Issue: "User not found"
**Solution:** Complete the profile page first

### Issue: "Assessment not found"
**Solution:** Add skills on assessment page before clicking proceed

### Issue: Still getting 500 error
**Solution:** Check server logs for detailed error message
- Look for "❌ Exception" in logs
- Check if OpenRouter API key is valid in `.env`
- Verify internet connection for API calls

### Issue: Fallback path always used
**Solution:** This means AI response parsing is failing
- Check OpenRouter API response format in logs
- May need to adjust prompt in `ai_generator.py`
- Fallback ensures system still works!

## Advanced Testing

### Test Different Domains
Try different career domains:
- Web Development
- Data Science
- Mobile Development
- Cybersecurity
- AI/ML

### Test Different Skill Levels
- All beginners (level 1-2)
- Mixed levels (1-5)
- All experts (level 4-5)

### Test Caching
1. Generate path for "Python, JavaScript, React"
2. Generate again with same skills → Should load from cache
3. Change one skill → Should generate new path

### Test Notes Generation
Go to `http://localhost:5000/notes.html`:
- Enter a topic (e.g., "React Hooks")
- Select level (Beginner/Intermediate/Advanced)
- Click "Generate Notes"
- Should see comprehensive study notes

## Success Criteria

✅ No 500 errors during assessment submission
✅ Learning path always generated (AI or fallback)
✅ Proper error messages if something fails
✅ Caching works (instant response on repeat)
✅ User redirected to learning-path.html
✅ Data persists in SQLite database

## Monitoring

### Watch for These Logs:
- ✅ "API call successful" - AI is working
- ✅ "Cache HIT" - Caching is working
- ✅ "Saved to SQLite" - Database is working
- ⚠️ "Using fallback" - AI parsing failed (but system works)
- ❌ "Exception" - Real error (check details)

### Database Check:
```bash
cd path_generator/data
sqlite3 users.db
SELECT * FROM users;
SELECT * FROM assessments;
SELECT * FROM learning_paths;
```

## Performance Notes

- **First generation:** 5-15 seconds (API call)
- **Cached generation:** < 1 second
- **Fallback generation:** < 1 second
- **Database save:** < 100ms

## Next Steps After Testing

1. If AI parsing consistently fails:
   - Review actual API responses in logs
   - Adjust prompt in `ai_generator.py` line 240
   - Consider different model or temperature

2. If everything works:
   - Test with real users
   - Monitor API usage and costs
   - Consider adding more fallback courses

3. Future enhancements:
   - Add retry logic for failed API calls
   - Implement rate limiting
   - Add more detailed progress indicators
   - Create admin dashboard for monitoring

---

**Ready to test!** 🚀
Open `http://localhost:5000/profile.html` and start the flow.
