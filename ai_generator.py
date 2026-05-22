"""
AI-Powered Learning Path Generator using OpenRouter API
with Firestore caching (primary) and SQLite fallback
"""

import os
import requests
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Try to initialize Firebase Admin (optional - graceful fallback)
db = None
use_firestore = False

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    # Try to initialize Firebase
    try:
        firebase_admin.get_app()
    except ValueError:
        # Use anonymous credentials for Firestore
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": os.getenv('FIREBASE_PROJECT_ID'),
            "private_key_id": "dummy",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC7W\n-----END PRIVATE KEY-----\n",
            "client_email": f"firebase-adminsdk@{os.getenv('FIREBASE_PROJECT_ID')}.iam.gserviceaccount.com",
            "client_id": "dummy",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        })
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    use_firestore = True
    print("✅ Firestore initialized successfully")
except Exception as e:
    print(f"⚠️ Firestore not available: {e}")
    print("📝 Falling back to SQLite for caching")
    use_firestore = False

# Initialize SQLite as fallback
sqlite_db_path = 'data/ai_cache.db'

def init_sqlite():
    """Initialize SQLite database for caching"""
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(sqlite_db_path)
    cursor = conn.cursor()
    
    # Create cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cache (
            cache_key TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            cached_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ SQLite cache initialized")

# Initialize SQLite if Firestore is not available
if not use_firestore:
    init_sqlite()

# OpenRouter API Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free')
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'


def generate_cache_key(user_profile, skills, domain):
    """Generate a unique cache key based on user profile and skills WITH LEVELS"""
    # Include skill levels in cache key to ensure different levels get different courses
    skill_details = []
    for skill in sorted(skills, key=lambda x: x['name']):
        skill_name = skill['name'].replace(' ', '_')
        skill_level = skill.get('level', 1)
        skill_details.append(f"{skill_name}_L{skill_level}")
    
    experience = user_profile.get('experienceLevel', 'beginner')
    cache_key = f"{domain}_{experience}_{'_'.join(skill_details)}"
    
    # Truncate if too long (max 200 chars for safety)
    if len(cache_key) > 200:
        cache_key = cache_key[:200]
    
    return cache_key


def check_sqlite_cache(cache_key):
    """Check if data exists in SQLite cache"""
    try:
        conn = sqlite3.connect(sqlite_db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT data FROM cache WHERE cache_key = ?', (cache_key,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            print(f"✅ SQLite Cache HIT: {cache_key}")
            return json.loads(result[0])
        else:
            print(f"❌ SQLite Cache MISS: {cache_key}")
            return None
    except Exception as e:
        print(f"⚠️ SQLite read error: {e}")
        return None


def save_to_sqlite(cache_key, data):
    """Save data to SQLite cache"""
    try:
        conn = sqlite3.connect(sqlite_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO cache (cache_key, data, cached_at)
            VALUES (?, ?, ?)
        ''', (cache_key, json.dumps(data), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Saved to SQLite: {cache_key}")
        return True
    except Exception as e:
        print(f"⚠️ SQLite write error: {e}")
        return False


def check_firestore_cache(cache_key):
    """Check if learning path exists in Firestore"""
    if not use_firestore or not db:
        return None
        
    try:
        doc_ref = db.collection('learning_paths').document(cache_key)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            print(f"✅ Firestore Cache HIT: {cache_key}")
            return data
        else:
            print(f"❌ Firestore Cache MISS: {cache_key}")
            return None
    except Exception as e:
        print(f"⚠️ Firestore read error: {e}")
        return None


def save_to_firestore(cache_key, learning_path_data):
    """Save generated learning path to Firestore"""
    if not use_firestore or not db:
        return False
        
    try:
        doc_ref = db.collection('learning_paths').document(cache_key)
        doc_ref.set({
            **learning_path_data,
            'cached_at': datetime.now().isoformat(),
            'cache_key': cache_key
        })
        print(f"✅ Saved to Firestore: {cache_key}")
        return True
    except Exception as e:
        print(f"⚠️ Firestore write error: {e}")
        return False


def check_cache(cache_key):
    """Check cache (Firestore first, then SQLite fallback)"""
    if use_firestore:
        cached = check_firestore_cache(cache_key)
        if cached:
            return cached
    
    # Fallback to SQLite
    return check_sqlite_cache(cache_key)


def save_to_cache(cache_key, data):
    """Save to cache (both Firestore and SQLite if available)"""
    saved = False
    
    if use_firestore:
        saved = save_to_firestore(cache_key, data)
    
    # Always save to SQLite as backup
    sqlite_saved = save_to_sqlite(cache_key, data)
    
    return saved or sqlite_saved


def call_openrouter_api(prompt):
    """Call OpenRouter API with Nvidia Nemotron model"""
    try:
        headers = {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:5000',
            'X-Title': 'Learning Path Generator'
        }
        
        payload = {
            'model': OPENROUTER_MODEL,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.5,  # Lower temperature for more focused responses
            'max_tokens': 1500  # Reduced to fit within model limits
        }
        
        print(f"🤖 Calling OpenRouter API with model: {OPENROUTER_MODEL}")
        print(f"🔑 API Key present: {bool(OPENROUTER_API_KEY)}")
        print(f"🔑 API Key length: {len(OPENROUTER_API_KEY) if OPENROUTER_API_KEY else 0}")
        
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        
        print(f"📡 Response status code: {response.status_code}")
        print(f"📡 Response headers: {dict(response.headers)}")
        
        response.raise_for_status()
        
        result = response.json()
        print(f"📦 Full API response structure: {json.dumps(result, indent=2)[:500]}...")
        
        # Check if response has expected structure
        if 'choices' not in result:
            print(f"❌ Unexpected response structure - missing 'choices' field")
            print(f"📄 Full response: {json.dumps(result, indent=2)}")
            return None
        
        if not result['choices'] or len(result['choices']) == 0:
            print(f"❌ Empty choices array in response")
            return None
        
        if 'message' not in result['choices'][0]:
            print(f"❌ Missing 'message' field in choices[0]")
            print(f"📄 choices[0]: {json.dumps(result['choices'][0], indent=2)}")
            return None
        
        if 'content' not in result['choices'][0]['message']:
            print(f"❌ Missing 'content' field in message")
            print(f"📄 message: {json.dumps(result['choices'][0]['message'], indent=2)}")
            return None
        
        content = result['choices'][0]['message']['content']
        
        # Check if content is None (happens when max_tokens is too low)
        if content is None:
            print(f"❌ Content is None - likely hit max_tokens limit")
            print(f"📄 finish_reason: {result['choices'][0].get('finish_reason', 'N/A')}")
            print(f"⚠️  Try increasing max_tokens in the API call")
            return None
        
        print(f"✅ API call successful")
        print(f"📝 Response length: {len(content)} characters")
        print(f"📝 Response preview: {content[:200]}...")
        return content
        
    except requests.exceptions.Timeout:
        print(f"❌ API call timed out after 60 seconds")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"📄 Response status: {e.response.status_code}")
        print(f"📄 Response body: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ API call failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"📄 Response: {e.response.text}")
        return None
    except KeyError as e:
        print(f"❌ KeyError accessing response: {e}")
        print(f"📄 Available keys: {result.keys() if 'result' in locals() else 'N/A'}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        print(f"📄 Traceback: {traceback.format_exc()}")
        return None


def create_fallback_learning_path(domain, experience, skills, skill_gaps):
    """
    Create a curated fallback learning path when AI fails
    Generates skill-specific courses based on user's actual skills
    """
    domain_clean = domain.replace('-', ' ').title()
    
    # Generate skill-specific courses based on user's skills
    skill_based_courses = []
    
    # Skill-specific course databases with DIRECT course URLs
    skill_course_map = {
        'React': {
            'Beginner': {'title': 'React Basics - The Complete Guide', 'url': 'https://www.udemy.com/course/react-the-complete-guide-incl-redux/', 'duration': '40 hours'},
            'Intermediate': {'title': 'React - The Complete Guide (incl Hooks, React Router, Redux)', 'url': 'https://www.udemy.com/course/react-the-complete-guide-incl-redux/', 'duration': '50 hours'},
            'Advanced': {'title': 'Advanced React and Redux', 'url': 'https://www.udemy.com/course/react-redux/', 'duration': '60 hours'}
        },
        'Python': {
            'Beginner': {'title': 'Complete Python Bootcamp: Go from zero to hero', 'url': 'https://www.udemy.com/course/complete-python-bootcamp/', 'duration': '30 hours'},
            'Intermediate': {'title': 'Python for Data Science and Machine Learning', 'url': 'https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/', 'duration': '40 hours'},
            'Advanced': {'title': 'Advanced Python Programming', 'url': 'https://www.udemy.com/course/python-beyond-the-basics-object-oriented-programming/', 'duration': '50 hours'}
        },
        'JavaScript': {
            'Beginner': {'title': 'The Complete JavaScript Course 2024: From Zero to Expert', 'url': 'https://www.udemy.com/course/the-complete-javascript-course/', 'duration': '35 hours'},
            'Intermediate': {'title': 'Modern JavaScript (Complete guide, from Novice to Ninja)', 'url': 'https://www.udemy.com/course/modern-javascript-from-novice-to-ninja/', 'duration': '45 hours'},
            'Advanced': {'title': 'JavaScript: Understanding the Weird Parts', 'url': 'https://www.udemy.com/course/understand-javascript/', 'duration': '55 hours'}
        },
        'Node.js': {
            'Beginner': {'title': 'The Complete Node.js Developer Course', 'url': 'https://www.udemy.com/course/the-complete-nodejs-developer-course-2/', 'duration': '30 hours'},
            'Intermediate': {'title': 'NodeJS - The Complete Guide (MVC, REST APIs, GraphQL)', 'url': 'https://www.udemy.com/course/nodejs-the-complete-guide/', 'duration': '40 hours'},
            'Advanced': {'title': 'Node.js, Express, MongoDB & More: The Complete Bootcamp', 'url': 'https://www.udemy.com/course/nodejs-express-mongodb-bootcamp/', 'duration': '50 hours'}
        },
        'SQL': {
            'Beginner': {'title': 'The Complete SQL Bootcamp: Go from Zero to Hero', 'url': 'https://www.udemy.com/course/the-complete-sql-bootcamp/', 'duration': '25 hours'},
            'Intermediate': {'title': 'SQL - MySQL for Data Analytics and Business Intelligence', 'url': 'https://www.udemy.com/course/sql-mysql-for-data-analytics-and-business-intelligence/', 'duration': '35 hours'},
            'Advanced': {'title': 'Advanced SQL: MySQL Data Analysis & Business Intelligence', 'url': 'https://www.udemy.com/course/advanced-sql-mysql-for-analytics-business-intelligence/', 'duration': '45 hours'}
        },
        'Docker': {
            'Beginner': {'title': 'Docker for the Absolute Beginner - Hands On', 'url': 'https://www.udemy.com/course/learn-docker/', 'duration': '20 hours'},
            'Intermediate': {'title': 'Docker Mastery: with Kubernetes +Swarm', 'url': 'https://www.udemy.com/course/docker-mastery/', 'duration': '30 hours'},
            'Advanced': {'title': 'Docker and Kubernetes: The Complete Guide', 'url': 'https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/', 'duration': '40 hours'}
        },
        'Java': {
            'Beginner': {'title': 'Java Programming Masterclass for Beginners', 'url': 'https://www.udemy.com/course/java-the-complete-java-developer-course/', 'duration': '35 hours'},
            'Intermediate': {'title': 'Java Programming: Complete Beginner to Advanced', 'url': 'https://www.udemy.com/course/java-programming-complete-beginner-to-advanced/', 'duration': '45 hours'},
            'Advanced': {'title': 'Java Multithreading, Concurrency & Performance', 'url': 'https://www.udemy.com/course/java-multithreading-concurrency-performance-optimization/', 'duration': '55 hours'}
        },
        'C++': {
            'Beginner': {'title': 'Beginning C++ Programming - From Beginner to Beyond', 'url': 'https://www.udemy.com/course/beginning-c-plus-plus-programming/', 'duration': '40 hours'},
            'Intermediate': {'title': 'Learn Advanced C++ Programming', 'url': 'https://www.udemy.com/course/learn-advanced-c-programming/', 'duration': '50 hours'},
            'Advanced': {'title': 'C++: From Beginner to Expert', 'url': 'https://www.udemy.com/course/video-course-c-from-beginner-to-expert/', 'duration': '60 hours'}
        },
        'HTML': {
            'Beginner': {'title': 'Build Responsive Real-World Websites with HTML and CSS', 'url': 'https://www.udemy.com/course/design-and-develop-a-killer-website-with-html5-and-css3/', 'duration': '20 hours'},
            'Intermediate': {'title': 'Modern HTML & CSS From The Beginning (Including Sass)', 'url': 'https://www.udemy.com/course/modern-html-css-from-the-beginning/', 'duration': '25 hours'},
            'Advanced': {'title': 'Advanced CSS and Sass: Flexbox, Grid, Animations', 'url': 'https://www.udemy.com/course/advanced-css-and-sass/', 'duration': '30 hours'}
        },
        'CSS': {
            'Beginner': {'title': 'CSS - The Complete Guide (incl. Flexbox, Grid & Sass)', 'url': 'https://www.udemy.com/course/css-the-complete-guide-incl-flexbox-grid-sass/', 'duration': '20 hours'},
            'Intermediate': {'title': 'Modern HTML & CSS From The Beginning', 'url': 'https://www.udemy.com/course/modern-html-css-from-the-beginning/', 'duration': '30 hours'},
            'Advanced': {'title': 'Advanced CSS and Sass: Flexbox, Grid, Animations', 'url': 'https://www.udemy.com/course/advanced-css-and-sass/', 'duration': '40 hours'}
        },
        'Machine Learning': {
            'Beginner': {'title': 'Machine Learning A-Z: Hands-On Python & R', 'url': 'https://www.udemy.com/course/machinelearning/', 'duration': '40 hours'},
            'Intermediate': {'title': 'Machine Learning, Data Science and Deep Learning', 'url': 'https://www.udemy.com/course/data-science-and-machine-learning-with-python-hands-on/', 'duration': '50 hours'},
            'Advanced': {'title': 'Advanced AI: Deep Reinforcement Learning', 'url': 'https://www.udemy.com/course/deep-reinforcement-learning-in-python/', 'duration': '60 hours'}
        },
        'Data Science': {
            'Beginner': {'title': 'Data Science Course: Complete Data Science Bootcamp', 'url': 'https://www.udemy.com/course/the-data-science-course-complete-data-science-bootcamp/', 'duration': '35 hours'},
            'Intermediate': {'title': 'Python for Data Science and Machine Learning', 'url': 'https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/', 'duration': '45 hours'},
            'Advanced': {'title': 'Data Science and Machine Learning Bootcamp', 'url': 'https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/', 'duration': '55 hours'}
        },
        'Angular': {
            'Beginner': {'title': 'Angular - The Complete Guide', 'url': 'https://www.udemy.com/course/the-complete-guide-to-angular-2/', 'duration': '35 hours'},
            'Intermediate': {'title': 'Angular & NodeJS - The MEAN Stack Guide', 'url': 'https://www.udemy.com/course/angular-2-and-nodejs-the-practical-guide/', 'duration': '45 hours'},
            'Advanced': {'title': 'Angular Advanced Masterclass', 'url': 'https://www.udemy.com/course/angular-advanced-masterclass/', 'duration': '55 hours'}
        },
        'Vue.js': {
            'Beginner': {'title': 'Vue - The Complete Guide (incl. Router & Composition API)', 'url': 'https://www.udemy.com/course/vuejs-2-the-complete-guide/', 'duration': '30 hours'},
            'Intermediate': {'title': 'Vue JS 3: Composition API (with Pinia, Firebase 9)', 'url': 'https://www.udemy.com/course/vue-js-3-composition-api/', 'duration': '40 hours'},
            'Advanced': {'title': 'Advanced Vue.js Features from the Ground Up', 'url': 'https://www.udemy.com/course/advanced-vuejs-features-from-the-ground-up/', 'duration': '50 hours'}
        },
        'MongoDB': {
            'Beginner': {'title': 'MongoDB - The Complete Developer\'s Guide', 'url': 'https://www.udemy.com/course/mongodb-the-complete-developers-guide/', 'duration': '25 hours'},
            'Intermediate': {'title': 'The Complete Developers Guide to MongoDB', 'url': 'https://www.udemy.com/course/the-complete-developers-guide-to-mongodb/', 'duration': '35 hours'},
            'Advanced': {'title': 'MongoDB Performance Tuning and Optimization', 'url': 'https://www.udemy.com/course/mongodb-performance/', 'duration': '45 hours'}
        }
    }
    
    for skill in skills[:6]:  # Top 6 skills
        skill_name = skill['name']
        skill_level = skill.get('level', 1)
        
        # Determine appropriate course level
        if skill_level <= 2:
            course_level = 'Beginner'
        elif skill_level == 3:
            course_level = 'Intermediate'
        else:
            course_level = 'Advanced'
        
        # Get skill-specific course or create generic one
        if skill_name in skill_course_map and course_level in skill_course_map[skill_name]:
            course_info = skill_course_map[skill_name][course_level]
            skill_based_courses.append({
                'title': course_info['title'],
                'provider': 'Udemy',
                'url': course_info['url'],
                'level': course_level,
                'duration': course_info['duration'],
                'description': f'Master {skill_name} from {course_level.lower()} level. Build real-world projects and gain practical experience.',
                'skills_covered': [skill_name]
            })
        else:
            # Generic fallback for unknown skills
            skill_based_courses.append({
                'title': f'{skill_name} - Complete {course_level} Guide',
                'provider': 'Udemy',
                'url': f'https://www.udemy.com/courses/search/?q={skill_name.replace(" ", "+")}',
                'level': course_level,
                'duration': f'{20 + skill_level * 10} hours',
                'description': f'Master {skill_name} from {course_level.lower()} level. Build real-world projects and gain practical experience.',
                'skills_covered': [skill_name]
            })
    
    # Generate skills list for frontend
    skills_list = [
        {
            'name': skill['name'],
            'description': f"Essential skill for {domain_clean}",
            'level': ['Beginner', 'Novice', 'Intermediate', 'Advanced', 'Expert'][min(skill.get('level', 1) - 1, 4)],
            'priority': 'High' if skill in skill_gaps[:2] else 'Medium'
        }
        for skill in skills[:5]
    ]
    
    fallback_path = {
        'skills': skills_list,
        'courses': skill_based_courses,
        'study_plan': {
            'week_1': f'Start with {skills[0]["name"] if skills else "fundamentals"} - review basics and set up development environment',
            'week_2': f'Deep dive into {skills[1]["name"] if len(skills) > 1 else "core concepts"} with hands-on exercises',
            'week_3': f'Build practical projects applying {skills[2]["name"] if len(skills) > 2 else "your skills"}',
            'week_4': f'Advanced topics in {domain_clean} and portfolio project completion'
        },
        'resources': [
            {
                'title': f'{domain_clean} Tutorial on YouTube',
                'type': 'Video',
                'url': 'https://www.youtube.com/results?search_query=' + domain.replace('-', '+'),
                'description': 'Video tutorials and walkthroughs'
            }
        ]
    }
    
    return fallback_path


def generate_learning_path_with_ai(user_profile, skills, skill_gaps, domain):
    """
    Generate learning path using AI with caching (Firestore or SQLite)
    Only calls API if not cached
    """
    
    # Generate cache key
    cache_key = generate_cache_key(user_profile, skills, domain)
    
    # Check cache first
    cached_data = check_cache(cache_key)
    if cached_data:
        return {
            'success': True,
            'from_cache': True,
            'learning_path': cached_data.get('learning_path'),
            'cache_key': cache_key
        }
    
    # Not in cache - generate with AI
    print(f"🚀 Generating new learning path with AI...")
    
    # Build prompt with DETAILED skill-specific requirements
    skill_list = ', '.join([s['name'] for s in skills])
    gap_list = ', '.join([g['name'] for g in skill_gaps])
    experience = user_profile.get('experienceLevel', 'beginner')
    
    # Create detailed skill breakdown for better course matching
    skill_details = []
    for skill in skills:
        skill_name = skill['name']
        skill_level = skill.get('level', 1)
        level_name = ['Beginner', 'Novice', 'Intermediate', 'Advanced', 'Expert'][min(skill_level - 1, 4)]
        skill_details.append(f"{skill_name} (Level {skill_level} - {level_name})")
    
    skill_breakdown = ' | '.join(skill_details)
    
    prompt = f"""Create a personalized learning path for {experience} level learner.

SKILLS TO DEVELOP (with current levels):
{skill_breakdown}

SKILL GAPS TO ADDRESS:
{gap_list}

DOMAIN: {domain}

IMPORTANT: Generate courses that are SPECIFIC to each skill listed above. Each course should clearly target ONE of the skills and match the appropriate difficulty level.

Return JSON:
{{
  "skills": [{{"name":"SkillName","description":"Why important","level":"Beginner/Intermediate/Advanced","priority":"High/Medium/Low"}}],
  "courses": [{{"title":"Course Name","provider":"Platform","url":"https://url","level":"Beginner/Intermediate/Advanced","duration":"Xh","description":"What you'll learn","skills_covered":["skill1","skill2"]}}],
  "study_plan": {{"week_1":"Plan","week_2":"Plan","week_3":"Plan","week_4":"Plan"}},
  "resources": [{{"title":"Name","type":"Type","url":"https://url","description":"Desc"}}]
}}

Generate 4-6 courses covering DIFFERENT skills from the list. Match course difficulty to skill level. Use real URLs from Coursera/Udemy/freeCodeCamp/YouTube."""
    
    # Call API
    ai_response = call_openrouter_api(prompt)
    
    # If API fails or returns None, use fallback immediately
    if not ai_response:
        print("⚠️ AI API returned None - using fallback learning path")
        fallback_path = create_fallback_learning_path(domain, experience, skills, skill_gaps)
        
        # Save fallback to cache
        save_to_cache(cache_key, {'learning_path': fallback_path})
        
        return {
            'success': True,
            'from_cache': False,
            'learning_path': fallback_path,
            'cache_key': cache_key,
            'warning': 'AI model hit token limit, using curated fallback path'
        }
    
    # Parse AI response
    try:
        # Extract JSON from response (handle markdown code blocks)
        cleaned_response = ai_response.strip()
        
        # Remove markdown code blocks if present
        if '```json' in cleaned_response:
            json_start = cleaned_response.find('```json') + 7
            json_end = cleaned_response.find('```', json_start)
            cleaned_response = cleaned_response[json_start:json_end].strip()
        elif '```' in cleaned_response:
            json_start = cleaned_response.find('```') + 3
            json_end = cleaned_response.find('```', json_start)
            cleaned_response = cleaned_response[json_start:json_end].strip()
        
        # Try to find JSON object boundaries if still not valid
        if not cleaned_response.startswith('{'):
            # Find first { and last }
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}')
            if start_idx != -1 and end_idx != -1:
                cleaned_response = cleaned_response[start_idx:end_idx+1]
        
        print(f"🔍 Cleaned response preview: {cleaned_response[:300]}...")
        
        learning_path = json.loads(cleaned_response)
        
        # Validate the structure has required fields
        if 'courses' not in learning_path:
            print("⚠️ AI response missing 'courses' field, adding fallback")
            learning_path['courses'] = []
        
        # Add skills field if missing (for frontend display)
        if 'skills' not in learning_path:
            print("⚠️ AI response missing 'skills' field, generating from user skills")
            learning_path['skills'] = [
                {
                    'name': skill['name'],
                    'description': f"Essential skill for {domain}",
                    'level': ['Beginner', 'Novice', 'Intermediate', 'Advanced', 'Expert'][min(skill.get('level', 1) - 1, 4)],
                    'priority': 'High' if skill in skill_gaps[:2] else 'Medium'
                }
                for skill in skills[:5]
            ]
        
        if 'study_plan' not in learning_path:
            print("⚠️ AI response missing 'study_plan' field, adding fallback")
            learning_path['study_plan'] = {
                'week_1': 'Start with foundational concepts',
                'week_2': 'Build on basics with practical exercises',
                'week_3': 'Dive into intermediate topics',
                'week_4': 'Work on advanced concepts and projects'
            }
        
        if 'resources' not in learning_path:
            print("⚠️ AI response missing 'resources' field, adding fallback")
            learning_path['resources'] = []
        
        # Save to cache (Firestore and/or SQLite)
        save_to_cache(cache_key, {'learning_path': learning_path})
        
        return {
            'success': True,
            'from_cache': False,
            'learning_path': learning_path,
            'cache_key': cache_key
        }
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse AI response as JSON: {e}")
        print(f"📄 Full raw response:\n{ai_response}")
        print(f"📄 Attempted to parse:\n{cleaned_response if 'cleaned_response' in locals() else 'N/A'}")
        
        # Use fallback instead of returning error
        print("⚠️ Using fallback learning path due to parsing error")
        fallback_path = create_fallback_learning_path(domain, experience, skills, skill_gaps)
        
        # Save fallback to cache
        save_to_cache(cache_key, {'learning_path': fallback_path})
        
        return {
            'success': True,
            'from_cache': False,
            'learning_path': fallback_path,
            'cache_key': cache_key,
            'warning': 'AI response could not be parsed, using curated fallback path'
        }


def generate_topic_notes_with_ai(topic, user_level='beginner'):
    """
    Generate study notes for a specific topic
    Cached in Firestore or SQLite
    """
    
    # Generate cache key for notes
    cache_key = f"notes_{topic.lower().replace(' ', '_')}_{user_level}"
    
    # Check cache
    cached_notes = check_cache(cache_key)
    if cached_notes:
        return {
            'success': True,
            'from_cache': True,
            'notes': cached_notes.get('notes'),
            'cache_key': cache_key
        }
    
    # Generate with AI
    print(f"📝 Generating notes for topic: {topic}")
    
    prompt = f"""
Create study notes for: "{topic}" ({user_level} level)

Return JSON:
{{
  "topic": "{topic}",
  "summary": "2-3 sentence overview",
  "key_concepts": [
    {{"concept": "Name", "explanation": "Clear explanation", "example": "Example"}}
  ],
  "learning_objectives": ["Objective 1", "Objective 2", "Objective 3"],
  "prerequisites": ["Prereq 1", "Prereq 2"],
  "practice_exercises": [
    {{"exercise": "Description", "difficulty": "Easy/Medium/Hard", "hint": "Hint"}}
  ],
  "additional_resources": [
    {{"title": "Resource", "url": "https://url.com", "type": "Type"}}
  ],
  "tips": ["Tip 1", "Tip 2", "Tip 3"]
}}

Make it practical and actionable for {user_level} learners.
"""
    
    ai_response = call_openrouter_api(prompt)
    
    if not ai_response:
        return {
            'success': False,
            'error': 'Failed to generate notes with AI'
        }
    
    try:
        # Parse response
        cleaned_response = ai_response.strip()
        
        # Remove markdown code blocks if present
        if '```json' in cleaned_response:
            json_start = cleaned_response.find('```json') + 7
            json_end = cleaned_response.find('```', json_start)
            cleaned_response = cleaned_response[json_start:json_end].strip()
        elif '```' in cleaned_response:
            json_start = cleaned_response.find('```') + 3
            json_end = cleaned_response.find('```', json_start)
            cleaned_response = cleaned_response[json_start:json_end].strip()
        
        # Try to find JSON object boundaries if still not valid
        if not cleaned_response.startswith('{'):
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}')
            if start_idx != -1 and end_idx != -1:
                cleaned_response = cleaned_response[start_idx:end_idx+1]
        
        print(f"🔍 Cleaned notes response preview: {cleaned_response[:200]}...")
        
        notes = json.loads(cleaned_response)
        
        # Validate structure
        if 'topic' not in notes:
            notes['topic'] = topic
        if 'summary' not in notes:
            notes['summary'] = f'Study notes for {topic}'
        if 'key_concepts' not in notes:
            notes['key_concepts'] = []
        
        # Save to cache (Firestore and/or SQLite)
        save_to_cache(cache_key, {'notes': notes})
        
        return {
            'success': True,
            'from_cache': False,
            'notes': notes,
            'cache_key': cache_key
        }
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse notes response: {e}")
        print(f"📄 Full raw response:\n{ai_response}")
        
        # Return enhanced fallback notes
        fallback_notes = {
            'topic': topic,
            'summary': f'This course covers essential concepts in {topic}. Perfect for {user_level} level learners looking to build strong foundations and practical skills.',
            'key_concepts': [
                {
                    'concept': 'Core Fundamentals',
                    'explanation': f'Understanding the basic principles and foundational concepts of {topic}. These form the building blocks for more advanced topics.',
                    'example': 'Start with simple examples and gradually progress to complex implementations.'
                },
                {
                    'concept': 'Practical Application',
                    'explanation': f'Learn how to apply {topic} concepts in real-world scenarios and projects.',
                    'example': 'Build hands-on projects that demonstrate your understanding and skills.'
                },
                {
                    'concept': 'Best Practices',
                    'explanation': f'Industry-standard approaches and patterns for working with {topic}.',
                    'example': 'Follow coding standards, write clean code, and use proper documentation.'
                }
            ],
            'learning_objectives': [
                f'Master the fundamental concepts of {topic}',
                f'Apply {topic} in practical projects and real-world scenarios',
                f'Understand best practices and industry standards',
                f'Build confidence through hands-on practice',
                f'Develop problem-solving skills related to {topic}'
            ],
            'prerequisites': [
                'Basic computer literacy',
                'Willingness to learn and practice',
                'Access to learning resources and development tools'
            ],
            'practice_exercises': [
                {
                    'exercise': f'Build a simple project using {topic} concepts',
                    'difficulty': 'Easy',
                    'hint': 'Start with the basics and add features incrementally'
                },
                {
                    'exercise': f'Complete coding challenges related to {topic}',
                    'difficulty': 'Medium',
                    'hint': 'Break down complex problems into smaller, manageable parts'
                },
                {
                    'exercise': f'Create a portfolio project showcasing {topic} skills',
                    'difficulty': 'Hard',
                    'hint': 'Focus on clean code, documentation, and user experience'
                }
            ],
            'additional_resources': [
                {
                    'title': f'{topic} Tutorial Videos',
                    'url': 'https://www.youtube.com/results?search_query=' + topic.replace(' ', '+'),
                    'type': 'Video'
                }
            ],
            'tips': [
                '💡 Practice coding every day, even if just for 30 minutes',
                '🚀 Build real projects to solidify your understanding',
                '👥 Join online communities and forums for support',
                '📚 Read documentation and explore official resources',
                '🎯 Set specific, achievable learning goals',
                '🔄 Review and refactor your code regularly',
                '❓ Don\'t hesitate to ask questions when stuck',
                '🏆 Celebrate small wins and track your progress'
            ]
        }
        
        print("⚠️ Using enhanced fallback notes due to parsing error")
        
        # Save fallback to cache
        save_to_cache(cache_key, {'notes': fallback_notes})
        
        return {
            'success': True,
            'from_cache': False,
            'notes': fallback_notes,
            'cache_key': cache_key,
            'warning': 'Using curated study notes (AI response was incomplete)'
        }



def generate_quiz_with_ai(topic, user_level='beginner'):
    """
    Generate a quiz for a specific topic
    Cached in Firestore or SQLite
    """
    
    # Generate cache key for quiz
    cache_key = f"quiz_{topic.lower().replace(' ', '_')}_{user_level}"
    
    # Check cache
    cached_quiz = check_cache(cache_key)
    if cached_quiz:
        return {
            'success': True,
            'from_cache': True,
            'quiz': cached_quiz.get('quiz'),
            'cache_key': cache_key
        }
    
    # Generate with AI
    print(f"📝 Generating quiz for topic: {topic}")
    
    prompt = f"""Create a quiz for: "{topic}" ({user_level} level)

Return JSON:
{{
  "title": "Quiz: {topic}",
  "questions": [
    {{
      "question": "Question text?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "Why this is correct"
    }}
  ]
}}

Create 5 multiple-choice questions for {user_level} learners. Make questions practical and test understanding.
"""
    
    ai_response = call_openrouter_api(prompt)
    
    if not ai_response:
        print("⚠️ AI API returned None - using fallback quiz")
        fallback_quiz = create_fallback_quiz(topic, user_level)
        save_to_cache(cache_key, {'quiz': fallback_quiz})
        return {
            'success': True,
            'from_cache': False,
            'quiz': fallback_quiz,
            'cache_key': cache_key,
            'warning': 'AI model hit token limit, using fallback quiz'
        }
    
    try:
        # Parse response
        cleaned_response = ai_response.strip()
        
        # Remove markdown code blocks if present
        if '```json' in cleaned_response:
            json_start = cleaned_response.find('```json') + 7
            json_end = cleaned_response.find('```', json_start)
            cleaned_response = cleaned_response[json_start:json_end].strip()
        elif '```' in cleaned_response:
            json_start = cleaned_response.find('```') + 3
            json_end = cleaned_response.find('```', json_start)
            cleaned_response = cleaned_response[json_start:json_end].strip()
        
        # Try to find JSON object boundaries
        if not cleaned_response.startswith('{'):
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}')
            if start_idx != -1 and end_idx != -1:
                cleaned_response = cleaned_response[start_idx:end_idx+1]
        
        print(f"🔍 Cleaned quiz response preview: {cleaned_response[:200]}...")
        
        quiz = json.loads(cleaned_response)
        
        # Validate structure
        if 'title' not in quiz:
            quiz['title'] = f'Quiz: {topic}'
        if 'questions' not in quiz or not quiz['questions']:
            quiz['questions'] = []
        
        # Save to cache
        save_to_cache(cache_key, {'quiz': quiz})
        
        return {
            'success': True,
            'from_cache': False,
            'quiz': quiz,
            'cache_key': cache_key
        }
        
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse quiz response: {e}")
        print(f"📄 Full raw response:\n{ai_response}")
        
        # Use fallback
        print("⚠️ Using fallback quiz due to parsing error")
        fallback_quiz = create_fallback_quiz(topic, user_level)
        save_to_cache(cache_key, {'quiz': fallback_quiz})
        
        return {
            'success': True,
            'from_cache': False,
            'quiz': fallback_quiz,
            'cache_key': cache_key,
            'warning': 'AI response could not be parsed, using fallback quiz'
        }


def create_fallback_quiz(topic, user_level):
    """Create fallback quiz when AI fails"""
    return {
        'title': f'Quiz: {topic}',
        'questions': [
            {
                'question': f'What is the main purpose of {topic}?',
                'options': [
                    'To solve specific problems in software development',
                    'To make code more complex',
                    'To replace all other technologies',
                    'None of the above'
                ],
                'correct_answer': 'To solve specific problems in software development',
                'explanation': f'{topic} is designed to address specific challenges and improve development efficiency.'
            },
            {
                'question': f'Which skill level is recommended before learning {topic}?',
                'options': [
                    'No prerequisites needed',
                    'Basic programming knowledge',
                    'Expert level in all technologies',
                    'PhD in Computer Science'
                ],
                'correct_answer': 'Basic programming knowledge',
                'explanation': 'Having foundational programming skills helps you learn new technologies more effectively.'
            },
            {
                'question': f'What is a best practice when working with {topic}?',
                'options': [
                    'Follow documentation and community guidelines',
                    'Ignore all conventions',
                    'Never test your code',
                    'Copy code without understanding'
                ],
                'correct_answer': 'Follow documentation and community guidelines',
                'explanation': 'Following best practices ensures maintainable and efficient code.'
            },
            {
                'question': f'How can you improve your skills in {topic}?',
                'options': [
                    'Build real projects and practice regularly',
                    'Only read theory',
                    'Avoid hands-on practice',
                    'Never ask for help'
                ],
                'correct_answer': 'Build real projects and practice regularly',
                'explanation': 'Practical experience is crucial for mastering any technology.'
            },
            {
                'question': f'What resource is most helpful for learning {topic}?',
                'options': [
                    'Official documentation and tutorials',
                    'Random blog posts only',
                    'Outdated books',
                    'Social media memes'
                ],
                'correct_answer': 'Official documentation and tutorials',
                'explanation': 'Official resources provide accurate and up-to-date information.'
            }
        ]
    }
