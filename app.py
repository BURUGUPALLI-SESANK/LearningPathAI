from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime
import json
import numpy as np
import re
from collections import Counter
from dotenv import load_dotenv
from ai_generator import generate_learning_path_with_ai, generate_topic_notes_with_ai, generate_quiz_with_ai
import user_database as udb

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS with proper configuration
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Data storage (in-memory for simplicity - use database in production)
learner_profiles = {}
skill_assessments = {}
learning_paths = {}
progress_data = {}
employability_scores = {}
adaptive_history = {}

# Load CSV datasets
def load_datasets():
    """Load students and courses CSV files"""
    students_file = 'data/students.csv'
    courses_file = 'data/courses.csv'
    
    students_df = None
    courses_df = None
    
    try:
        if os.path.exists(students_file):
            students_df = pd.read_csv(students_file)
            print(f"Loaded {len(students_df)} student records")
    except Exception as e:
        print(f"Error loading students.csv: {e}")
    
    try:
        if os.path.exists(courses_file):
            courses_df = pd.read_csv(courses_file)
            print(f"Loaded {len(courses_df)} course records")
    except Exception as e:
        print(f"Error loading courses.csv: {e}")
    
    return students_df, courses_df

# Initialize datasets
students_df, courses_df = load_datasets()

def analyze_skill_gaps(assessment_skills, target_domain):
    """
    Improved skill gap analysis with flexible domain matching
    """

    domain_requirements = {
        'computer-science': ['Programming Fundamentals', 'Data Structures', 'Algorithms', 'Software Engineering'],
        'data-science': ['Python', 'Statistics', 'Machine Learning', 'Data Analysis'],
        'web-development': ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js', 'Database Design'],
        'mobile-development': ['Mobile App Design', 'iOS Development', 'Android Development', 'UI/UX', 'API Integration'],
        'cybersecurity': ['Network Security', 'Ethical Hacking', 'Cryptography', 'Security Analysis'],
        'ai-ml': ['Python', 'Machine Learning', 'Deep Learning', 'Neural Networks'],
        'business': ['Business Strategy', 'Marketing', 'Finance', 'Management'],
        'design': ['UI/UX Design', 'Graphic Design', 'Design Tools', 'User Research'],
        'marketing': ['Digital Marketing', 'SEO', 'Content Marketing', 'Analytics']
    }

    # Normalize domain (VERY IMPORTANT FIX)
    normalized_domain = target_domain.lower().strip().replace(" ", "-")

    required_skills = []

    # Flexible domain matching
    for domain in domain_requirements:
        if domain in normalized_domain or normalized_domain in domain:
            required_skills = domain_requirements[domain]
            break

    # If no match found → fallback to data-science (safe default)
    if not required_skills:
        required_skills = domain_requirements['data-science']

    skill_gaps = []

    for skill in required_skills:
        found = False

        for assessed_skill in assessment_skills:
            if skill.lower() in assessed_skill['name'].lower():
                found = True

                if assessed_skill['level'] <= 2:
                    skill_gaps.append({
                        'name': skill,
                        'current_level': assessed_skill['level'],
                        'recommended_level': 4,
                        'priority': 'High'
                    })
                break

        if not found:
            skill_gaps.append({
                'name': skill,
                'current_level': 0,
                'recommended_level': 3,
                'priority': 'High'
            })

    return skill_gaps


def recommend_courses(learner_profile, assessment_skills, skill_gaps):
    """
    Enhanced ML-based course recommendation with custom text similarity
    (Works without scikit-learn using word matching algorithm)
    """

    recommendations = []

    if courses_df is not None and not courses_df.empty:

        target_domain = learner_profile.get('currentDomain', '').lower()

        # Flexible filtering
        if 'domain' in courses_df.columns:
            domain_courses = courses_df[
                courses_df['domain'].str.lower().str.contains(target_domain, na=False)
            ]
        else:
            domain_courses = courses_df

        # If no match → use all courses
        if domain_courses.empty:
            domain_courses = courses_df

        # Custom ML-like recommendation using word matching
        try:
            # Create learner skill profile text
            learner_skills_text = ' '.join([skill['name'].lower() for skill in assessment_skills])
            learner_skills_text += ' ' + ' '.join([gap['name'].lower() for gap in skill_gaps])
            learner_skills_text += ' ' + target_domain.replace('-', ' ')
            
            learner_words = set(re.findall(r'\w+', learner_skills_text.lower()))
            
            # Calculate similarity for each course
            for idx, course in domain_courses.iterrows():
                course_text = str(course.get('skills', '')) + ' ' + str(course.get('title', '')) + ' ' + str(course.get('description', ''))
                course_words = set(re.findall(r'\w+', course_text.lower()))
                
                # Calculate Jaccard similarity (intersection over union)
                if len(learner_words) > 0 and len(course_words) > 0:
                    intersection = len(learner_words & course_words)
                    union = len(learner_words | course_words)
                    ml_score = (intersection / union) * 10 if union > 0 else 0
                else:
                    ml_score = 0
                
                # Rule-based adjustments
                rule_score = 0
                course_skills = str(course.get('skills', '')).lower()
                
                # Skill gap match
                for gap in skill_gaps:
                    if gap['name'].lower() in course_skills:
                        rule_score += 2
                
                # Experience level match
                experience = learner_profile.get('experienceLevel', 'beginner').lower()
                course_level = str(course.get('level', 'beginner')).lower()
                if experience == course_level:
                    rule_score += 1.5
                
                # Learning style match
                learning_style = learner_profile.get('learningStyle', 'video').lower()
                course_format = str(course.get('format', 'video')).lower()
                if learning_style in course_format:
                    rule_score += 1
                
                # Combined score (70% ML, 30% rules)
                final_score = (ml_score * 0.7) + (rule_score * 0.3)
                
                if final_score >= 1:
                    recommendations.append({
                        'title': course.get('title', 'Unknown Course'),
                        'provider': course.get('provider', 'Unknown'),
                        'level': course.get('level', 'Beginner'),
                        'duration': course.get('duration', 'N/A'),
                        'rating': float(course.get('rating', 0)) if pd.notna(course.get('rating')) else 0,
                        'students': course.get('students', 'N/A'),
                        'description': course.get('description', ''),
                        'score': round(final_score, 2),
                        'ml_score': round(ml_score, 2),
                        'relevance': 'High' if final_score >= 7 else 'Medium' if final_score >= 4 else 'Low'
                    })
        
        except Exception as e:
            print(f"ML recommendation error: {e}, falling back to rule-based")
            # Fallback to original rule-based if ML fails
            for _, course in domain_courses.iterrows():
                score = 0
                course_skills = str(course.get('skills', '')).lower()
                
                for gap in skill_gaps:
                    if gap['name'].lower() in course_skills:
                        score += 3
                
                experience = learner_profile.get('experienceLevel', 'beginner').lower()
                course_level = str(course.get('level', 'beginner')).lower()
                if experience == course_level:
                    score += 2
                
                learning_style = learner_profile.get('learningStyle', 'video').lower()
                course_format = str(course.get('format', 'video')).lower()
                if learning_style in course_format:
                    score += 1
                
                if score >= 1:
                    recommendations.append({
                        'title': course.get('title', 'Unknown Course'),
                        'provider': course.get('provider', 'Unknown'),
                        'level': course.get('level', 'Beginner'),
                        'duration': course.get('duration', 'N/A'),
                        'rating': float(course.get('rating', 0)) if pd.notna(course.get('rating')) else 0,
                        'students': course.get('students', 'N/A'),
                        'description': course.get('description', ''),
                        'score': score,
                        'relevance': 'Medium'
                    })

        recommendations.sort(key=lambda x: x['score'], reverse=True)

        if recommendations:
            return recommendations[:10]

    # Guaranteed fallback if CSV fails
    return [{
        'title': 'Python for Data Science',
        'provider': 'Udemy',
        'level': 'Beginner',
        'duration': '30 hours',
        'rating': 4.6,
        'students': '100,000+',
        'description': 'Complete Python guide for Data Science',
        'score': 5,
        'relevance': 'Medium'
    }]


# API Endpoints

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'AI-Powered Personalized Learning Path Generator API',
        'version': '1.0.0',
        'endpoints': {
            'POST /register': 'Register learner profile',
            'POST /assessment': 'Submit skill assessment',
            'POST /generate-path': 'Generate personalized learning path',
            'GET /dashboard/<user_id>': 'Get dashboard data'
        }
    })

@app.route('/firebase-config', methods=['GET'])
def get_firebase_config():
    """Serve Firebase configuration from environment variables"""
    try:
        firebase_config = {
            'apiKey': os.getenv('FIREBASE_API_KEY'),
            'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
            'projectId': os.getenv('FIREBASE_PROJECT_ID'),
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
            'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
            'appId': os.getenv('FIREBASE_APP_ID'),
            'measurementId': os.getenv('FIREBASE_MEASUREMENT_ID')
        }
        
        # Check if all required config values are present
        if not all(firebase_config.values()):
            return jsonify({
                'error': 'Firebase configuration incomplete. Please check .env file.'
            }), 500
        
        return jsonify(firebase_config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ai-generate-path', methods=['POST'])
def ai_generate_path():
    """Generate learning path using AI with Firestore caching"""
    try:
        data = request.json
        user_id = data.get('userId')
        force_regenerate = data.get('forceRegenerate', False)
        
        print(f"🚀 AI Generate Path request for user: {user_id}, force={force_regenerate}")
        
        if not user_id:
            return jsonify({'error': 'Missing userId'}), 400
        
        # Get user profile and assessment
        if user_id not in learner_profiles:
            return jsonify({'error': 'User not found. Please register first.'}), 404
        
        if user_id not in skill_assessments:
            return jsonify({'error': 'Assessment not found. Please submit assessment first.'}), 404
        
        # Load user data from database if not in memory
        if user_id not in learner_profiles:
            profile = udb.get_user(user_id)
            if profile:
                learner_profiles[user_id] = profile
            else:
                return jsonify({'error': 'User not found. Please register first.'}), 404
        
        if user_id not in skill_assessments:
            assessment = udb.get_assessment(user_id)
            if assessment:
                skill_assessments[user_id] = assessment
            else:
                return jsonify({'error': 'Assessment not found. Please submit assessment first.'}), 404
        
        profile = learner_profiles[user_id]
        assessment = skill_assessments[user_id]
        
        print(f"📊 Profile domain: {profile.get('currentDomain')}")
        print(f"📊 Skills count: {len(assessment['skills'])}")
        
        # Analyze skill gaps
        skill_gaps = analyze_skill_gaps(
            assessment['skills'],
            profile.get('currentDomain', '')
        )
        
        print(f"📊 Skill gaps identified: {len(skill_gaps)}")
        
        # Generate with AI (cached in SQLite/Firestore)
        result = generate_learning_path_with_ai(
            profile,
            assessment['skills'],
            skill_gaps,
            profile.get('currentDomain', '')
        )
        
        print(f"✅ AI generation result: success={result['success']}, from_cache={result.get('from_cache', False)}")
        
        if not result['success']:
            error_msg = result.get('error', 'AI generation failed')
            print(f"❌ AI generation failed: {error_msg}")
            return jsonify({'error': error_msg}), 500
        
        learning_path_data = {
            'userId': user_id,
            'generatedAt': datetime.now().isoformat(),
            'ai_generated': True,
            'from_cache': result['from_cache'],
            'cache_key': result.get('cache_key'),
            **result['learning_path']
        }
        
        # Store in memory
        learning_paths[user_id] = learning_path_data
        
        # Save to database
        udb.save_learning_path(user_id, learning_path_data, ai_generated=True)
        
        # Calculate and save employability
        employability_data = calculate_employability_score(
            user_id, profile, assessment, skill_gaps, 
            result['learning_path'].get('courses', [])
        )
        employability_scores[user_id] = employability_data
        udb.save_employability(user_id, employability_data)
        
        print(f"✅ Learning path saved successfully for user {user_id}")
        
        response_data = {
            'success': True,
            'from_cache': result['from_cache'],
            'message': 'Loaded from cache' if result['from_cache'] else 'Generated with AI',
            'learningPath': learning_path_data,
            'employabilityScore': employability_data
        }
        
        if 'warning' in result:
            response_data['warning'] = result['warning']
        
        return jsonify(response_data), 200
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Exception in ai_generate_path: {str(e)}")
        print(f"📄 Full traceback:\n{error_trace}")
        return jsonify({
            'error': str(e),
            'details': 'Check server logs for more information'
        }), 500

@app.route('/ai-generate-notes', methods=['POST'])
def ai_generate_notes():
    """Generate study notes for a topic using AI with caching"""
    try:
        data = request.json
        topic = data.get('topic')
        user_level = data.get('level', 'beginner')
        
        if not topic:
            return jsonify({'error': 'Missing topic'}), 400
        
        # Generate notes with AI (cached in Firestore)
        result = generate_topic_notes_with_ai(topic, user_level)
        
        if not result['success']:
            return jsonify({'error': result.get('error', 'Notes generation failed')}), 500
        
        return jsonify({
            'success': True,
            'from_cache': result['from_cache'],
            'message': 'Loaded from cache' if result['from_cache'] else 'Generated with AI',
            'notes': result['notes'],
            'cache_key': result.get('cache_key')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ai-generate-quiz', methods=['POST'])
def ai_generate_quiz():
    """Generate a quiz for a topic using AI with caching"""
    try:
        data = request.json
        topic = data.get('topic')
        user_level = data.get('level', 'beginner')
        
        if not topic:
            return jsonify({'error': 'Missing topic'}), 400
        
        # Generate quiz with AI (cached in Firestore/SQLite)
        result = generate_quiz_with_ai(topic, user_level)
        
        if not result['success']:
            return jsonify({'error': result.get('error', 'Quiz generation failed')}), 500
        
        response_data = {
            'success': True,
            'from_cache': result['from_cache'],
            'message': 'Loaded from cache' if result['from_cache'] else 'Generated with AI',
            'quiz': result['quiz'],
            'cache_key': result.get('cache_key')
        }
        
        if 'warning' in result:
            response_data['warning'] = result['warning']
        
        return jsonify(response_data), 200
        
    except Exception as e:
        import traceback
        print(f"❌ Exception in ai_generate_quiz: {str(e)}")
        print(f"📄 Traceback:\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/clear-cache', methods=['POST'])
def clear_cache():
    """Clear AI cache to force fresh generation"""
    try:
        import os
        cache_file = 'data/ai_cache.db'
        
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print(f"✅ Cache cleared: {cache_file}")
            return jsonify({'success': True, 'message': 'Cache cleared successfully'}), 200
        else:
            print(f"⚠️ No cache file found: {cache_file}")
            return jsonify({'success': True, 'message': 'No cache to clear'}), 200
            
    except Exception as e:
        print(f"❌ Error clearing cache: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/register', methods=['POST'])
def register_learner():
    """Register a new learner profile"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['fullName', 'age', 'educationLevel', 'currentDomain', 
                          'careerGoal', 'experienceLevel', 'learningStyle', 'weeklyStudyHours']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if custom user ID is provided (e.g. from Google Auth)
        user_id = data.get('userId')
        if not user_id:
            user_id = f"user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        profile_data = {
            'userId': user_id,
            **data,
            'registeredAt': datetime.now().isoformat()
        }
        
        # Store in memory (for backward compatibility)
        learner_profiles[user_id] = profile_data
        
        # Save to database
        udb.save_user(
            user_id=user_id,
            email=data.get('email', user_id),
            full_name=data['fullName'],
            profile_data=profile_data
        )
        
        return jsonify({
            'success': True,
            'message': 'Learner profile registered successfully',
            'userId': user_id,
            'profile': profile_data
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile/<user_id>', methods=['GET'])
def get_learner_profile(user_id):
    """Retrieve learner profile by user ID"""
    try:
        # Try memory first
        if user_id in learner_profiles:
            return jsonify({
                'success': True,
                'profile': learner_profiles[user_id]
            }), 200
        return jsonify({
            'success': False,
            'error': 'Profile not found'
        }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/assessment', methods=['POST'])
def submit_assessment():
    """Submit skill assessment"""
    try:
        data = request.json
        
        # Validate required fields
        if 'userId' not in data:
            return jsonify({'error': 'Missing userId'}), 400
        
        if 'skills' not in data or not isinstance(data['skills'], list):
            return jsonify({'error': 'Missing or invalid skills array'}), 400
        
        user_id = data['userId']
        
        # Check if user exists (memory or database)
        if user_id not in learner_profiles:
            profile = udb.get_user(user_id)
            if profile:
                learner_profiles[user_id] = profile
            else:
                return jsonify({'error': 'User not found. Please register first.'}), 404
        
        # Calculate assessment metrics
        skills = data['skills']
        total_skills = len(skills)
        total_score = sum(skill.get('level', 0) for skill in skills)
        average_level = total_score / total_skills if total_skills > 0 else 0
        
        assessment_data = {
            'userId': user_id,
            'skills': skills,
            'totalSkills': total_skills,
            'totalScore': total_score,
            'averageLevel': round(average_level, 2),
            'assessedAt': datetime.now().isoformat()
        }
        
        # Store in memory
        skill_assessments[user_id] = assessment_data
        
        # Save to database
        udb.save_assessment(user_id, assessment_data)
        
        return jsonify({
            'success': True,
            'message': 'Skill assessment submitted successfully',
            'assessment': assessment_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-path', methods=['POST'])
def generate_learning_path():
    """Generate personalized learning path"""
    try:
        data = request.json
        
        # Validate required fields
        if 'userId' not in data:
            return jsonify({'error': 'Missing userId'}), 400
        
        user_id = data['userId']
        
        # Validate user exists
        if user_id not in learner_profiles:
            return jsonify({'error': 'User not found. Please register first.'}), 404
        
        # Validate assessment exists
        if user_id not in skill_assessments:
            return jsonify({'error': 'Assessment not found. Please submit assessment first.'}), 404
        
        # Get learner profile and assessment
        profile = learner_profiles[user_id]
        assessment = skill_assessments[user_id]
        
        # Perform skill gap analysis
        skill_gaps = analyze_skill_gaps(
            assessment['skills'],
            profile.get('currentDomain', '')
        )
        
        # Get recommended skills (from skill gaps)
        recommended_skills = [
            {
                'name': gap['name'],
                'description': f"Develop {gap['name']} skills to reach level {gap['recommended_level']}",
                'level': 'Beginner' if gap['current_level'] == 0 else 
                        'Intermediate' if gap['current_level'] <= 2 else 'Advanced',
                'priority': gap['priority']
            }
            for gap in skill_gaps
        ]
        
        # Get course recommendations
        recommended_courses = recommend_courses(profile, assessment['skills'], skill_gaps)
        
        # Generate learning path
        learning_path = {
            'userId': user_id,
            'generatedAt': datetime.now().isoformat(),
            'skills': recommended_skills,
            'courses': recommended_courses,
            'totalSkills': len(recommended_skills),
            'totalCourses': len(recommended_courses),
            'skillGaps': skill_gaps
        }
        
        # Store learning path
        learning_paths[user_id] = learning_path
        
        # Calculate employability score
        employability_data = calculate_employability_score(user_id, profile, assessment, skill_gaps, recommended_courses)
        employability_scores[user_id] = employability_data
        
        # Initialize adaptive tracking
        if user_id not in adaptive_history:
            adaptive_history[user_id] = {
                'total_sessions': 0,
                'avg_completion': 0,
                'velocity': 'Not Started',
                'recommendation': 'Begin your learning journey!',
                'last_updated': datetime.now().isoformat()
            }
        
        # Initialize progress data
        if user_id not in progress_data:
            progress_data[user_id] = {
                'skills': [
                    {'name': skill['name'], 'progress': 0, 'level': skill['level']}
                    for skill in recommended_skills
                ],
                'courses': [
                    {'title': course['title'], 'provider': course['provider'], 
                     'progress': 0, 'status': 'not-started'}
                    for course in recommended_courses
                ]
            }
        
        return jsonify({
            'success': True,
            'message': 'Learning path generated successfully',
            'learningPath': learning_path,
            'employabilityScore': employability_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard/<user_id>', methods=['GET'])
def get_dashboard_data(user_id):
    """Get dashboard data for a user"""
    try:
        # Check if user exists
        if user_id not in learner_profiles:
            return jsonify({'error': 'User not found'}), 404
        
        # Get progress data
        user_progress = progress_data.get(user_id, {
            'skills': [],
            'courses': []
        })
        
        # Calculate statistics
        total_courses = len(user_progress['courses'])
        completed_courses = len([c for c in user_progress['courses'] if c.get('progress', 0) == 100])
        in_progress_courses = len([c for c in user_progress['courses'] 
                                  if 0 < c.get('progress', 0) < 100])
        
        overall_progress = 0
        if total_courses > 0:
            total_progress = sum(c.get('progress', 0) for c in user_progress['courses'])
            overall_progress = round(total_progress / total_courses, 1)
        
        # Calculate skill statistics
        total_skills = len(user_progress['skills'])
        mastered_skills = len([s for s in user_progress['skills'] if s.get('progress', 0) >= 80])
        
        # Calculate average skill level
        avg_level = 0
        if total_skills > 0:
            level_values = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
            total_level = sum(level_values.get(s.get('level', 'Beginner'), 1) 
                            for s in user_progress['skills'])
            avg_level = round(total_level / total_skills, 1)
        
        # Calculate hours completed (assuming 40 hours per course on average)
        hours_completed = round(sum(c.get('progress', 0) / 100 * 40 for c in user_progress['courses']), 1)
        
        dashboard_data = {
            'userId': user_id,
            'statistics': {
                'totalCourses': total_courses,
                'completedCourses': completed_courses,
                'inProgressCourses': in_progress_courses,
                'overallProgress': overall_progress
            },
            'skills': user_progress['skills'],
            'courses': user_progress['courses'],
            'summary': {
                'totalSkills': total_skills,
                'masteredSkills': mastered_skills,
                'averageSkillLevel': avg_level,
                'hoursCompleted': hours_completed,
                'completionRate': overall_progress
            }
        }
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update-progress', methods=['POST'])
def update_progress():
    """Update progress for skills or courses with adaptive learning"""
    try:
        data = request.json
        
        if 'userId' not in data:
            return jsonify({'error': 'Missing userId'}), 400
        
        user_id = data['userId']
        
        if user_id not in progress_data:
            return jsonify({'error': 'User progress not found'}), 404
        
        # Update skill progress
        if 'skillProgress' in data:
            for skill_update in data['skillProgress']:
                for skill in progress_data[user_id]['skills']:
                    if skill['name'] == skill_update['name']:
                        skill['progress'] = skill_update['progress']
                        break
        
        # Update course progress
        if 'courseProgress' in data:
            for course_update in data['courseProgress']:
                for course in progress_data[user_id]['courses']:
                    if course['title'] == course_update['title']:
                        course['progress'] = course_update['progress']
                        if course_update['progress'] == 100:
                            course['status'] = 'completed'
                        elif course_update['progress'] > 0:
                            course['status'] = 'in-progress'
                        break
        
        # Adaptive Learning: Analyze performance and update recommendations
        adaptive_update = analyze_and_adapt(user_id)
        
        # Recalculate employability score
        if user_id in learner_profiles and user_id in skill_assessments:
            profile = learner_profiles[user_id]
            assessment = skill_assessments[user_id]
            skill_gaps = []
            if user_id in learning_paths:
                skill_gaps = learning_paths[user_id].get('skillGaps', [])
            courses = learning_paths[user_id].get('courses', []) if user_id in learning_paths else []
            
            employability_data = calculate_employability_score(user_id, profile, assessment, skill_gaps, courses)
            employability_scores[user_id] = employability_data
        
        return jsonify({
            'success': True,
            'message': 'Progress updated successfully',
            'progress': progress_data[user_id],
            'adaptiveUpdate': adaptive_update,
            'employabilityScore': employability_scores.get(user_id, {})
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def analyze_and_adapt(user_id):
    """
    Analyze learner performance and provide adaptive recommendations
    """
    if user_id not in progress_data:
        return {'message': 'No progress data available'}
    
    user_progress = progress_data[user_id]
    courses = user_progress.get('courses', [])
    skills = user_progress.get('skills', [])
    
    # Calculate metrics
    total_courses = len(courses)
    completed_courses = len([c for c in courses if c.get('progress', 0) == 100])
    in_progress_courses = len([c for c in courses if 0 < c.get('progress', 0) < 100])
    
    avg_course_completion = sum(c.get('progress', 0) for c in courses) / total_courses if total_courses > 0 else 0
    avg_skill_progress = sum(s.get('progress', 0) for s in skills) / len(skills) if skills else 0
    
    # Determine learning velocity
    if avg_course_completion >= 70:
        velocity = "Fast - Excellent pace!"
        recommendation = "You're progressing rapidly! Consider taking on advanced topics or side projects."
    elif avg_course_completion >= 40:
        velocity = "Steady - Good progress"
        recommendation = "Maintain your current pace. Focus on completing in-progress courses."
    elif avg_course_completion >= 15:
        velocity = "Slow - Needs boost"
        recommendation = "Try dedicating more time daily. Break courses into smaller milestones."
    else:
        velocity = "Just Started"
        recommendation = "Begin with your first course! Set a goal to complete 20% this week."
    
    # Update adaptive history
    if user_id not in adaptive_history:
        adaptive_history[user_id] = {}
    
    adaptive_history[user_id].update({
        'total_sessions': adaptive_history[user_id].get('total_sessions', 0) + 1,
        'avg_completion': round(avg_course_completion, 1),
        'velocity': velocity,
        'recommendation': recommendation,
        'last_updated': datetime.now().isoformat(),
        'completed_courses': completed_courses,
        'in_progress_courses': in_progress_courses
    })
    
    # Check if path needs regeneration
    should_regenerate = False
    regeneration_reason = ""
    
    if completed_courses >= total_courses * 0.8 and total_courses > 0:
        should_regenerate = True
        regeneration_reason = "You've completed most courses! Time to generate an advanced learning path."
    elif avg_skill_progress >= 80:
        should_regenerate = True
        regeneration_reason = "Your skills have significantly improved! Consider updating your path for advanced topics."
    
    return {
        'velocity': velocity,
        'recommendation': recommendation,
        'avg_completion': round(avg_course_completion, 1),
        'should_regenerate': should_regenerate,
        'regeneration_reason': regeneration_reason,
        'metrics': {
            'completed': completed_courses,
            'in_progress': in_progress_courses,
            'total': total_courses
        }
    }

@app.route('/employability/<user_id>', methods=['GET'])
def get_employability_score(user_id):
    """Get employability score for a user"""
    try:
        if user_id not in employability_scores:
            return jsonify({
                'success': False,
                'error': 'Employability score not calculated yet. Generate a learning path first.'
            }), 404
        
        return jsonify({
            'success': True,
            'employability': employability_scores[user_id]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/adaptive-insights/<user_id>', methods=['GET'])
def get_adaptive_insights(user_id):
    """Get adaptive learning insights for a user"""
    try:
        if user_id not in adaptive_history:
            return jsonify({
                'success': False,
                'error': 'No adaptive learning data available yet.'
            }), 404
        
        return jsonify({
            'success': True,
            'insights': adaptive_history[user_id]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Feedback and Chatbot API Implementation
FEEDBACKS_FILE = 'data/feedbacks.csv'

def init_feedback_csv():
    """Initialize feedbacks.csv with sample records if it doesn't exist"""
    if os.path.exists(FEEDBACKS_FILE):
        try:
            df = pd.read_csv(FEEDBACKS_FILE)
            if not df.empty:
                return
        except Exception:
            pass
            
    # Sample feedbacks
    samples = [
        {"feedback_id": "fb_1", "name": "Emily Carter", "overall_rating": 5, "recommendation_rating": 5, "customization_rating": 5, "comments": "Absolutely loved the personalized web development roadmap! The recommended courses match my pace perfectly.", "requested_features": "Study Planner,AI Chatbot", "sentiment": "Positive", "date": "2026-05-10T10:15:30"},
        {"feedback_id": "fb_2", "name": "Liam Davies", "overall_rating": 4, "recommendation_rating": 4, "customization_rating": 5, "comments": "The skill gap analysis showed me exactly what I was missing. It would be amazing if I could schedule these study hours directly in a calendar.", "requested_features": "Study Planner", "sentiment": "Positive", "date": "2026-05-11T14:22:11"},
        {"feedback_id": "fb_3", "name": "Sophia Martinez", "overall_rating": 3, "recommendation_rating": 3, "customization_rating": 4, "comments": "Good recommendations, but some of the intermediate courses require more coding experience. I would love a Certificate of Completion to show on my resume.", "requested_features": "Certifications,Job Matching", "sentiment": "Neutral", "date": "2026-05-12T09:05:00"},
        {"feedback_id": "fb_4", "name": "Noah Brooks", "overall_rating": 5, "recommendation_rating": 5, "customization_rating": 4, "comments": "The UI looks stunning. Very smooth transitions and helpful links. An AI Chatbot or Study Buddy would make this the ultimate learning portal.", "requested_features": "AI Chatbot", "sentiment": "Positive", "date": "2026-05-13T16:40:45"},
        {"feedback_id": "fb_5", "name": "Olivia Turner", "overall_rating": 4, "recommendation_rating": 5, "customization_rating": 3, "comments": "I registered for Data Science and got highly relevant Coursera classes. Can you add direct job referrals or matching with tech companies?", "requested_features": "Job Matching", "sentiment": "Positive", "date": "2026-05-14T11:55:00"},
        {"feedback_id": "fb_6", "name": "Aiden Vance", "overall_rating": 2, "recommendation_rating": 2, "customization_rating": 3, "comments": "I felt a bit overwhelmed by the 40 hours of study required per week. I need a study planner to help me break it down.", "requested_features": "Study Planner", "sentiment": "Negative", "date": "2026-05-15T18:10:20"},
        {"feedback_id": "fb_7", "name": "Isabella Chen", "overall_rating": 5, "recommendation_rating": 4, "customization_rating": 5, "comments": "Best personalized path generator I've used. Very robust. Adding certification options would be a great BMC addition.", "requested_features": "Certifications", "sentiment": "Positive", "date": "2026-05-16T12:00:10"},
        {"feedback_id": "fb_8", "name": "Lucas Grey", "overall_rating": 4, "recommendation_rating": 3, "customization_rating": 4, "comments": "Nice layout. The courses seem high quality. Having a mentor connect feature would elevate it.", "requested_features": "Mentors", "sentiment": "Positive", "date": "2026-05-16T15:30:25"},
        {"feedback_id": "fb_9", "name": "Mia Jenkins", "overall_rating": 3, "recommendation_rating": 4, "customization_rating": 3, "comments": "It generated a web-dev path. I was hoping for more practice-based text resources. A chatbot would help me find those.", "requested_features": "AI Chatbot,Study Planner", "sentiment": "Neutral", "date": "2026-05-17T08:45:15"},
        {"feedback_id": "fb_10", "name": "Ethan Hunt", "overall_rating": 5, "recommendation_rating": 5, "customization_rating": 5, "comments": "Brilliant project. Adding a premium model with professional certifications and direct job matches would make this a viable business.", "requested_features": "Certifications,Job Matching", "sentiment": "Positive", "date": "2026-05-17T20:18:40"},
        {"feedback_id": "fb_11", "name": "Charlotte Webb", "overall_rating": 4, "recommendation_rating": 4, "customization_rating": 4, "comments": "Helped me structure my learning for the summer. It would be helpful to sync study hours directly with my Google calendar.", "requested_features": "Study Planner", "sentiment": "Positive", "date": "2026-05-18T10:05:00"},
        {"feedback_id": "fb_12", "name": "Benjamin Cole", "overall_rating": 5, "recommendation_rating": 4, "customization_rating": 4, "comments": "Simple and effective. Love the progress tracking! A chatbot assistant would make navigation even easier.", "requested_features": "AI Chatbot", "sentiment": "Positive", "date": "2026-05-18T14:32:00"},
        {"feedback_id": "fb_13", "name": "Amelia Vance", "overall_rating": 3, "recommendation_rating": 3, "customization_rating": 3, "comments": "Okay experience, but I need more mock tests and practice codes. Certificates would be cool.", "requested_features": "Certifications", "sentiment": "Neutral", "date": "2026-05-19T09:12:30"},
        {"feedback_id": "fb_14", "name": "Daniel Craig", "overall_rating": 4, "recommendation_rating": 5, "customization_rating": 4, "comments": "Recommended courses match my goal perfectly. Job matches in my area would be extremely helpful.", "requested_features": "Job Matching", "sentiment": "Positive", "date": "2026-05-19T16:48:00"},
        {"feedback_id": "fb_15", "name": "Harper Lee", "overall_rating": 5, "recommendation_rating": 5, "customization_rating": 5, "comments": "The skill assessment was simple and the recommendations are exactly what I needed. I am following the path daily!", "requested_features": "Study Planner,Certifications", "sentiment": "Positive", "date": "2026-05-20T11:20:15"},
        {"feedback_id": "fb_16", "name": "Alexander Great", "overall_rating": 4, "recommendation_rating": 3, "customization_rating": 5, "comments": "Good path. Can we get an interactive code editor or interactive chat to ask about specific syntax?", "requested_features": "AI Chatbot", "sentiment": "Positive", "date": "2026-05-20T17:02:40"},
        {"feedback_id": "fb_17", "name": "Evelyn Stone", "overall_rating": 2, "recommendation_rating": 3, "customization_rating": 2, "comments": "The suggested courses are too long. 50 hours of video is hard to manage. A study planner is critical for me.", "requested_features": "Study Planner", "sentiment": "Negative", "date": "2026-05-20T19:55:00"},
        {"feedback_id": "fb_18", "name": "Sebastian Bach", "overall_rating": 4, "recommendation_rating": 4, "customization_rating": 4, "comments": "Well integrated dashboard. Tracking my hours helps. Adding job matches for intermediate roles would be great.", "requested_features": "Job Matching", "sentiment": "Positive", "date": "2026-05-21T08:30:12"},
        {"feedback_id": "fb_19", "name": "Zoe Saldana", "overall_rating": 5, "recommendation_rating": 5, "customization_rating": 4, "comments": "Incredible customization! It really takes my educational background into account. Certifications + Job portals are logical next steps.", "requested_features": "Certifications,Job Matching", "sentiment": "Positive", "date": "2026-05-21T10:14:50"},
        {"feedback_id": "fb_20", "name": "William Shakespeare", "overall_rating": 4, "recommendation_rating": 4, "customization_rating": 5, "comments": "A very useful helper in my self-taught learning journey. A virtual study buddy to ask questions would be an excellent feature.", "requested_features": "AI Chatbot", "sentiment": "Positive", "date": "2026-05-21T12:05:33"}
    ]
    
    os.makedirs(os.path.dirname(FEEDBACKS_FILE), exist_ok=True)
    df = pd.DataFrame(samples)
    df.to_csv(FEEDBACKS_FILE, index=False)
    print(f"Generated {len(samples)} sample feedback records in {FEEDBACKS_FILE}")

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json or {}
        name = data.get('name', 'Anonymous')
        overall = int(data.get('overall_rating', 5))
        reco = int(data.get('recommendation_rating', 5))
        cust = int(data.get('customization_rating', 5))
        comments = data.get('comments', '')
        features = data.get('requested_features', '')
        
        # Heuristic sentiment analysis
        if overall >= 4:
            sentiment = "Positive"
        elif overall == 3:
            sentiment = "Neutral"
        else:
            sentiment = "Negative"
            
        new_feedback = {
            'feedback_id': f"fb_{int(datetime.now().timestamp())}",
            'name': name,
            'overall_rating': overall,
            'recommendation_rating': reco,
            'customization_rating': cust,
            'comments': comments,
            'requested_features': features,
            'sentiment': sentiment,
            'date': datetime.now().isoformat()
        }
        
        # Load and append
        if os.path.exists(FEEDBACKS_FILE):
            try:
                df = pd.read_csv(FEEDBACKS_FILE)
            except Exception:
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()
            
        df = pd.concat([df, pd.DataFrame([new_feedback])], ignore_index=True)
        df.to_csv(FEEDBACKS_FILE, index=False)
        
        return jsonify({'success': True, 'message': 'Feedback submitted successfully', 'feedback': new_feedback}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/feedbacks', methods=['GET'])
def get_feedbacks():
    try:
        if not os.path.exists(FEEDBACKS_FILE):
            init_feedback_csv()
            
        df = pd.read_csv(FEEDBACKS_FILE)
        df['comments'] = df['comments'].fillna('')
        df['requested_features'] = df['requested_features'].fillna('')
        
        total = len(df)
        if total == 0:
            return jsonify({
                'success': True,
                'metrics': {
                    'total_feedbacks': 0,
                    'avg_overall': 0,
                    'avg_recommendation': 0,
                    'avg_customization': 0,
                    'nps': 0,
                    'sentiment': {'Positive': 0, 'Neutral': 0, 'Negative': 0},
                    'features': {}
                },
                'feedbacks': []
            })
            
        avg_overall = round(float(df['overall_rating'].mean()), 2)
        avg_reco = round(float(df['recommendation_rating'].mean()), 2)
        avg_cust = round(float(df['customization_rating'].mean()), 2)
        
        # NPS Score: promoters % (4-5) - detractors % (1-2)
        promoters = len(df[df['overall_rating'] >= 4])
        detractors = len(df[df['overall_rating'] <= 2])
        nps = round(((promoters - detractors) / total) * 100, 1)
        
        sentiment_counts = df['sentiment'].value_counts().to_dict()
        for s in ['Positive', 'Neutral', 'Negative']:
            if s not in sentiment_counts:
                sentiment_counts[s] = 0
                
        # Features counts
        features_dict = {}
        for _, row in df.iterrows():
            features_list = str(row['requested_features']).split(',')
            for f in features_list:
                f_clean = f.strip()
                if f_clean and f_clean != 'nan' and f_clean != '':
                    features_dict[f_clean] = features_dict.get(f_clean, 0) + 1
                    
        feedbacks_list = df.to_dict(orient='records')
        
        return jsonify({
            'success': True,
            'metrics': {
                'total_feedbacks': total,
                'avg_overall': avg_overall,
                'avg_recommendation': avg_reco,
                'avg_customization': avg_cust,
                'nps': nps,
                'sentiment': sentiment_counts,
                'features': features_dict
            },
            'feedbacks': feedbacks_list
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analytics-data', methods=['GET'])
def get_analytics_data():
    try:
        # Load students data
        students_file = 'data/students.csv'
        students_list = []
        if os.path.exists(students_file):
            students_df = pd.read_csv(students_file)
            students_list = students_df.to_dict(orient='records')
            
        # Add registered students from runtime memory
        for user_id, profile in learner_profiles.items():
            exists = False
            for s in students_list:
                if str(s.get('student_id')) == str(user_id) or s.get('name') == profile.get('fullName'):
                    exists = True
                    break
            if not exists:
                students_list.append({
                    'student_id': user_id,
                    'name': profile.get('fullName'),
                    'age': profile.get('age'),
                    'education_level': profile.get('educationLevel'),
                    'domain': profile.get('currentDomain'),
                    'experience_level': profile.get('experienceLevel'),
                    'learning_style': profile.get('learningStyle', 'video'),
                    'weekly_hours': profile.get('weeklyStudyHours', 10)
                })
                
        df = pd.DataFrame(students_list)
        if df.empty:
            return jsonify({
                'success': True,
                'domains': {},
                'experience': {},
                'education': {},
                'styles': {},
                'age_groups': {},
                'hours_vs_level': [],
                'total_students': 0
            })
            
        # Normalize and fillna
        df['domain'] = df['domain'].str.lower().str.strip()
        df['experience_level'] = df['experience_level'].str.lower().str.strip()
        df['education_level'] = df['education_level'].fillna("Bachelor's Degree").str.strip()
        
        if 'learning_style' not in df.columns:
            df['learning_style'] = 'video'
        else:
            df['learning_style'] = df['learning_style'].fillna('video')
            
        if 'weekly_hours' not in df.columns:
            # check if weeklyStudyHours was used instead
            if 'weeklyStudyHours' in df.columns:
                df['weekly_hours'] = df['weeklyStudyHours'].fillna(10)
            else:
                df['weekly_hours'] = 10
        else:
            df['weekly_hours'] = df['weekly_hours'].fillna(10)
            
        domains = df['domain'].value_counts().to_dict()
        experience = df['experience_level'].value_counts().to_dict()
        education = df['education_level'].value_counts().to_dict()
        styles = df['learning_style'].value_counts().to_dict()
        
        # Age distribution
        ages = pd.to_numeric(df['age'], errors='coerce').fillna(22).tolist()
        age_groups = {
            'Under 20': len([a for a in ages if a < 20]),
            '20-24': len([a for a in ages if 20 <= a <= 24]),
            '25-29': len([a for a in ages if 25 <= a <= 29]),
            '30+': len([a for a in ages if a >= 30])
        }
        
        # Weekly study hours list
        hours_vs_level = []
        for _, row in df.iterrows():
            hours_vs_level.append({
                'name': row.get('name', 'Student'),
                'hours': int(row.get('weekly_hours', 10)),
                'level': str(row.get('experience_level', 'beginner')).capitalize(),
                'domain': str(row.get('domain', 'other')).capitalize()
            })
            
        return jsonify({
            'success': True,
            'domains': domains,
            'experience': experience,
            'education': education,
            'styles': styles,
            'age_groups': age_groups,
            'hours_vs_level': hours_vs_level,
            'total_students': len(df)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json or {}
        message = str(data.get('message', '')).lower().strip()
        user_name = data.get('userName', 'Learner')
        user_domain = data.get('userDomain', 'web-development')
        user_id = data.get('userId', None)
        
        if not message:
            return jsonify({'response': "Hello! I am your AI Study Copilot. Ask me anything about your learning path, courses, or schedule!"})
        
        # Enhanced intelligent tutoring with context awareness
        response = generate_intelligent_response(message, user_name, user_domain, user_id)
            
        return jsonify({'response': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_intelligent_response(message, user_name, user_domain, user_id):
    """Enhanced intelligent tutoring system with adaptive responses"""
    
    # Get user context if available
    user_context = ""
    if user_id and user_id in learner_profiles:
        profile = learner_profiles[user_id]
        exp_level = profile.get('experienceLevel', 'beginner')
        user_context = f" (Experience: {exp_level})"
    
    # Check for employability query
    if "employability" in message or "job ready" in message or "hire" in message or "readiness" in message:
        if user_id and user_id in employability_scores:
            score_data = employability_scores[user_id]
            return f"Your current **Employability Score** is **{score_data['overall_score']}/100**! 📊\n\n" \
                   f"Breakdown:\n" \
                   f"• Skills Mastery: {score_data['skills_score']}/40\n" \
                   f"• Course Completion: {score_data['completion_score']}/30\n" \
                   f"• Industry Alignment: {score_data['industry_score']}/30\n\n" \
                   f"Status: {score_data['readiness_level']}\n" \
                   f"Recommendation: {score_data['recommendation']}"
        else:
            return "Complete your skill assessment and learning path to get your personalized Employability Score! 📊"
    
    # Adaptive learning check
    if "progress" in message or "how am i doing" in message or "performance" in message:
        if user_id and user_id in adaptive_history:
            history = adaptive_history[user_id]
            return f"Great question! Based on your learning analytics:\n\n" \
                   f"• Total study sessions: {history.get('total_sessions', 0)}\n" \
                   f"• Average completion rate: {history.get('avg_completion', 0)}%\n" \
                   f"• Learning velocity: {history.get('velocity', 'Steady')}\n" \
                   f"• Recommended adjustment: {history.get('recommendation', 'Keep up the great work!')}\n\n" \
                   f"Your path will auto-adapt based on your performance! 🚀"
        else:
            return "Start tracking your progress to get personalized performance insights! 📈"
    
    # Domain-specific intelligent responses
    if "hello" in message or "hi" in message or "hey" in message:
        return f"Hi {user_name}{user_context}! 👋 I am your AI Study Tutor. I can help answer coding questions, recommend studies, or help you schedule your study hours. What are we studying today?"
    
    elif "react" in message:
        return "React is a fantastic component-based UI library! ⚛️ To learn React effectively, start with:\n1. HTML5 & CSS3 layouts\n2. ES6+ JavaScript concepts (destructuring, map/filter, modules, async/await)\n3. React basics (components, props, state)\n4. React Hooks (useState, useEffect)\n\nI recommend taking the 'React - The Complete Guide' course. Would you like me to outline a weekly schedule for React?"
    
    elif "javascript" in message or "js" in message:
        return "JavaScript is the backbone of web development! 🌐 Key areas to focus on: variables, functions, DOM manipulation, event listeners, array methods, and async operations (Promises, fetch). For a structured study, I suggest devoting at least 6-8 hours a week, starting with 'Complete JavaScript Course 2024'."
    
    elif "python" in message:
        return "Python is the leading language for Data Science and AI! 🐍 It is known for its clean syntax. Start with variables, lists, dictionaries, functions, and file handling. Then, learn libraries like Pandas, NumPy, and Matplotlib. I suggest 'Python for Data Science' on Udemy as a starting point!"
    
    elif "data science" in message or "machine learning" in message or "ml" in message:
        return "Data Science combines programming, statistics, and domain expertise. 📊 The ideal learning progression is:\n1. Python coding fundamentals\n2. SQL & Database Design (for retrieving data)\n3. Data Analysis & Visualization (Pandas, Seaborn)\n4. Machine Learning models (Scikit-learn)\n\nLet me know if you would like me to set up a Data Science learning plan!"
    
    elif "hours" in message or "time" in message or "study plan" in message or "schedule" in message or "calendar" in message:
        return "Managing your time is key to learning success! 📅 In our new **Study Planner** tab on the **Demo Hub**, you can generate an automatic daily schedule based on your weekly study hours. For example, if you study 10 hours a week, devoting 2 hours every weekday allows your brain to absorb information much better than cramming on weekends!"
    
    elif "job" in message or "career" in message or "work" in message:
        return "Our Business Model Canvas (BMC) incorporates direct job matching! 💼 Once you complete your path, you will get matches for job roles matching your skill level (e.g. Junior Web Developer). You can preview these jobs in the **Jobs & Certificate** section of the **Demo Hub**. Keep learning to unlock more job referrals!"
    
    elif "certificate" in message or "certification" in message:
        return "Earning certificates is a great way to validate your skills! 📜 Once you finish a course or complete a path, you can claim your Certificate of Completion on the **Demo Hub** page. It can be added directly to your LinkedIn or resume!"
    
    elif "thank" in message:
        return f"You are very welcome, {user_name}! 😊 I am always here to support your learning journey. Let me know if you need anything else!"
    
    else:
        return f"That's a great question, {user_name}! 💡 Learning about '{message}' is highly valuable in today's tech market. I recommend starting with beginner courses in that domain and dedicating around 1.5 hours daily. Ask me for specific resource recommendations if you want to dive deeper!"

def calculate_employability_score(user_id, profile, assessment, skill_gaps, courses):
    """
    Calculate comprehensive employability score based on multiple factors
    """
    
    # 1. Skills Mastery Score (40 points)
    total_skills = assessment.get('totalSkills', 0)
    avg_level = assessment.get('averageLevel', 0)
    skills_score = min(40, (avg_level / 5.0) * 40) if total_skills > 0 else 0
    
    # Penalty for skill gaps
    gap_penalty = min(10, len(skill_gaps) * 2)
    skills_score = max(0, skills_score - gap_penalty)
    
    # 2. Course Completion Score (30 points)
    if user_id in progress_data:
        user_progress = progress_data[user_id]
        total_courses = len(user_progress.get('courses', []))
        if total_courses > 0:
            total_progress = sum(c.get('progress', 0) for c in user_progress['courses'])
            completion_score = (total_progress / (total_courses * 100)) * 30
        else:
            completion_score = 0
    else:
        completion_score = 0
    
    # 3. Industry Alignment Score (30 points)
    domain = profile.get('currentDomain', '').lower()
    experience = profile.get('experienceLevel', 'beginner').lower()
    
    # Domain demand multiplier
    high_demand_domains = ['web-development', 'data-science', 'ai-ml', 'cybersecurity']
    domain_multiplier = 1.2 if domain in high_demand_domains else 1.0
    
    # Experience level bonus
    exp_bonus = {'beginner': 5, 'intermediate': 15, 'advanced': 25}.get(experience, 5)
    
    # Course quality (based on ML relevance scores)
    avg_course_relevance = sum(c.get('score', 0) for c in courses) / len(courses) if courses else 0
    relevance_score = min(10, avg_course_relevance)
    
    industry_score = min(30, (exp_bonus + relevance_score) * domain_multiplier)
    
    # Overall Score
    overall_score = round(skills_score + completion_score + industry_score, 1)
    
    # Readiness Level
    if overall_score >= 80:
        readiness_level = "Job Ready - Highly Employable"
        recommendation = "You're ready to apply for positions! Update your resume and start applying."
    elif overall_score >= 60:
        readiness_level = "Nearly Ready - Good Progress"
        recommendation = "Complete 2-3 more courses and practice projects to boost your score."
    elif overall_score >= 40:
        readiness_level = "Developing - Keep Learning"
        recommendation = "Focus on completing your learning path and building practical projects."
    else:
        readiness_level = "Early Stage - Foundation Building"
        recommendation = "Continue with your skill assessments and complete beginner courses first."
    
    return {
        'overall_score': overall_score,
        'skills_score': round(skills_score, 1),
        'completion_score': round(completion_score, 1),
        'industry_score': round(industry_score, 1),
        'readiness_level': readiness_level,
        'recommendation': recommendation,
        'calculated_at': datetime.now().isoformat()
    }

@app.route('/update-daily-tasks', methods=['POST'])
def update_daily_tasks():
    """Update daily tasks progress"""
    try:
        data = request.json
        user_id = data.get('userId')
        tasks = data.get('tasks', {})
        progress = data.get('progress', 0)
        completed = data.get('completedTasks', 0)
        total = data.get('totalTasks', 0)
        
        if not user_id:
            return jsonify({'error': 'Missing userId'}), 400
        
        # Store in memory
        if user_id not in progress_data:
            progress_data[user_id] = {}
        
        progress_data[user_id]['daily_tasks'] = {
            'tasks': tasks,
            'progress': progress,
            'completed': completed,
            'total': total,
            'updated_at': datetime.now().isoformat()
        }
        
        # Save to database
        try:
            udb.save_daily_tasks(user_id, tasks, progress, completed, total)
        except Exception as e:
            print(f"Warning: Could not save to database: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Daily tasks updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-daily-tasks/<user_id>', methods=['GET'])
def get_daily_tasks(user_id):
    """Get daily tasks for a user"""
    try:
        # Check memory first
        if user_id in progress_data and 'daily_tasks' in progress_data[user_id]:
            return jsonify({
                'success': True,
                'dailyTasks': progress_data[user_id]['daily_tasks']
            }), 200
        
        # Check database
        try:
            tasks_data = udb.get_daily_tasks(user_id)
            if tasks_data:
                return jsonify({
                    'success': True,
                    'dailyTasks': tasks_data
                }), 200
        except Exception as e:
            print(f"Warning: Could not load from database: {e}")
        
        return jsonify({
            'success': False,
            'error': 'No daily tasks found'
        }), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-learning-path/<user_id>', methods=['GET'])
def get_learning_path(user_id):
    """Get learning path for a user"""
    try:
        # Check memory first
        if user_id in learning_paths:
            return jsonify({
                'success': True,
                'learningPath': learning_paths[user_id]
            }), 200
        
        # Check database
        path = udb.get_learning_path(user_id)
        if path:
            learning_paths[user_id] = path  # Cache in memory
            return jsonify({
                'success': True,
                'learningPath': path
            }), 200
        
        return jsonify({
            'success': False,
            'error': 'Learning path not found. Please generate one first.'
        }), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ai-chat', methods=['POST'])
def ai_chat():
    """AI Chat endpoint for the chatbot tutor - Uses REAL AI"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        user_id = data.get('userId')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Get REAL user context
        user_name = "Learner"
        user_domain = "general"
        user_level = "beginner"
        user_courses = []
        user_progress = {}
        
        if user_id:
            # Get profile
            if user_id in learner_profiles:
                profile = learner_profiles[user_id]
                user_name = profile.get('fullName', 'Learner').split()[0]
                user_domain = profile.get('currentDomain', 'general')
                user_level = profile.get('experienceLevel', 'beginner')
            else:
                # Try loading from database
                profile = udb.get_user(user_id)
                if profile:
                    learner_profiles[user_id] = profile
                    user_name = profile.get('fullName', 'Learner').split()[0]
                    user_domain = profile.get('currentDomain', 'general')
                    user_level = profile.get('experienceLevel', 'beginner')
            
            # Get learning path
            if user_id in learning_paths:
                user_courses = learning_paths[user_id].get('courses', [])
            else:
                path = udb.get_learning_path(user_id)
                if path:
                    learning_paths[user_id] = path
                    user_courses = path.get('courses', [])
            
            # Get progress
            if user_id in progress_data:
                user_progress = progress_data[user_id]
        
        # Try using OpenRouter API for REAL AI responses
        try:
            import requests
            
            openrouter_key = os.getenv('OPENROUTER_API_KEY')
            
            if openrouter_key:
                # Build context-aware prompt
                context = f"""You are an AI Learning Tutor helping {user_name}.
User Profile:
- Domain: {user_domain}
- Experience Level: {user_level}
- Current Courses: {len(user_courses)} courses in learning path

Provide helpful, encouraging, and specific guidance. Keep responses concise (2-3 paragraphs max).
"""
                
                # Call OpenRouter API
                response = requests.post(
                    'https://openrouter.ai/api/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {openrouter_key}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': 'nvidia/llama-3.1-nemotron-70b-instruct',
                        'messages': [
                            {'role': 'system', 'content': context},
                            {'role': 'user', 'content': message}
                        ],
                        'max_tokens': 500,
                        'temperature': 0.7
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    ai_response = response.json()['choices'][0]['message']['content']
                    return jsonify({
                        'success': True,
                        'response': ai_response,
                        'source': 'openrouter'
                    }), 200
        except Exception as e:
            print(f"OpenRouter API error: {e}")
            # Fall through to intelligent fallback
        
        # Intelligent fallback with REAL user data
        response = generate_intelligent_response(message, user_name, user_domain, user_id)
        
        return jsonify({
            'success': True,
            'response': response,
            'source': 'fallback'
        }), 200
        
    except Exception as e:
        import traceback
        print(f"❌ AI Chat error: {str(e)}")
        print(f"📄 Traceback:\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static HTML, JS, CSS files from root directory"""
    return send_from_directory('.', filename)

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Initialize feedbacks
    init_feedback_csv()
    
    print("=" * 80)
    print("🚀 AI-Powered Personalized Learning Path Generator")
    print("=" * 80)
    print("\n📊 API Endpoints:")
    print("  POST /register - Register learner profile")
    print("  POST /assessment - Submit skill assessment")
    print("  POST /generate-path - Generate learning path")
    print("  GET /dashboard/<user_id> - Get dashboard data")
    print("  POST /update-progress - Update progress")
    print("  POST /submit-feedback - Submit customer feedback")
    print("  GET /feedbacks - Get feedback analytics")
    print("  GET /analytics-data - Get customer behaviour analytics")
    print("  POST /chat - AI Study Tutor Chatbot")
    print("  GET /employability/<user_id> - Get employability score (NEW)")
    print("  GET /adaptive-insights/<user_id> - Get adaptive learning insights (NEW)")
    
    print("\n🌐 Frontend Pages:")
    print("  http://localhost:5000/index.html - Home Page")
    print("  http://localhost:5000/profile.html - Create Profile")
    print("  http://localhost:5000/assessment.html - Skill Assessment")
    print("  http://localhost:5000/learning-path.html - Learning Path")
    print("  http://localhost:5000/dashboard.html - Progress Dashboard")
    print("  http://localhost:5000/employability.html - Employability Score (NEW)")
    print("  http://localhost:5000/demo-hub.html - Demo Hub")
    
    print("\n✨ New Features Implemented:")
    print("  ✅ ML-Based Course Recommendations (Jaccard Similarity)")
    print("  ✅ Employability Score System (0-100 scale)")
    print("  ✅ Adaptive Learning Engine (Performance tracking)")
    print("  ✅ Enhanced Intelligent Tutoring (Context-aware chatbot)")
    
    print("\n" + "=" * 80)
    print("Server starting on http://localhost:5000")
    print("=" * 80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

