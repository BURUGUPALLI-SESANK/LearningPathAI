"""
Test the full learning path generation flow
"""

import requests
import json
import time

API_BASE = 'http://localhost:5000'

print("=" * 80)
print("🧪 Full Flow Test - AI Learning Path Generation")
print("=" * 80)

# Test 1: Register a test user
print("\n1️⃣ Registering test user...")
user_data = {
    'fullName': 'Test User',
    'age': 25,
    'educationLevel': 'Bachelor',
    'currentDomain': 'web-development',
    'careerGoal': 'Full Stack Developer',
    'experienceLevel': 'intermediate',
    'learningStyle': 'video',
    'weeklyStudyHours': 10,
    'email': 'test@example.com'
}

try:
    response = requests.post(f'{API_BASE}/register', json=user_data, timeout=10)
    if response.status_code == 201:
        result = response.json()
        user_id = result['userId']
        print(f"✅ User registered: {user_id}")
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"📄 {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test 2: Submit assessment
print("\n2️⃣ Submitting skill assessment...")
assessment_data = {
    'userId': user_id,
    'skills': [
        {'name': 'JavaScript', 'level': 3},
        {'name': 'React', 'level': 2},
        {'name': 'Node.js', 'level': 2},
        {'name': 'HTML/CSS', 'level': 4}
    ]
}

try:
    response = requests.post(f'{API_BASE}/assessment', json=assessment_data, timeout=10)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Assessment submitted")
        print(f"   Total skills: {result['assessment']['totalSkills']}")
        print(f"   Average level: {result['assessment']['averageLevel']}")
    else:
        print(f"❌ Assessment failed: {response.status_code}")
        print(f"📄 {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test 3: Generate AI learning path
print("\n3️⃣ Generating AI learning path...")
print("⏳ This may take 5-15 seconds...")

try:
    start_time = time.time()
    response = requests.post(
        f'{API_BASE}/ai-generate-path',
        json={'userId': user_id},
        timeout=60
    )
    elapsed = time.time() - start_time
    
    print(f"⏱️  Request took {elapsed:.2f} seconds")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Learning path generated!")
        print(f"   From cache: {result.get('from_cache', False)}")
        print(f"   Message: {result.get('message', 'N/A')}")
        
        if 'warning' in result:
            print(f"⚠️  Warning: {result['warning']}")
        
        learning_path = result.get('learningPath', {})
        
        # Show courses
        courses = learning_path.get('courses', [])
        print(f"\n📚 Courses ({len(courses)}):")
        for i, course in enumerate(courses[:3], 1):
            print(f"   {i}. {course.get('title', 'N/A')}")
            print(f"      Provider: {course.get('provider', 'N/A')}")
            print(f"      Level: {course.get('level', 'N/A')}")
            print(f"      URL: {course.get('url', 'N/A')}")
        
        if len(courses) > 3:
            print(f"   ... and {len(courses) - 3} more courses")
        
        # Show study plan
        study_plan = learning_path.get('study_plan', {})
        if study_plan:
            print(f"\n📅 Study Plan:")
            for week, plan in list(study_plan.items())[:2]:
                print(f"   {week}: {plan[:60]}...")
        
        # Show resources
        resources = learning_path.get('resources', [])
        if resources:
            print(f"\n🔗 Resources ({len(resources)}):")
            for i, resource in enumerate(resources[:2], 1):
                print(f"   {i}. {resource.get('title', 'N/A')} ({resource.get('type', 'N/A')})")
        
        # Show employability score
        employability = result.get('employabilityScore', {})
        if employability:
            print(f"\n💼 Employability Score:")
            print(f"   Overall: {employability.get('overallScore', 'N/A')}/100")
            print(f"   Level: {employability.get('level', 'N/A')}")
        
        print(f"\n{'=' * 80}")
        print("✅ SUCCESS! Full flow completed successfully!")
        print("=" * 80)
        
    else:
        print(f"❌ Learning path generation failed: {response.status_code}")
        print(f"📄 Response: {response.text}")
        exit(1)
        
except requests.exceptions.Timeout:
    print(f"❌ Request timed out after 60 seconds")
    print(f"   The AI generation is taking too long")
    exit(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    print(f"📄 Traceback:\n{traceback.format_exc()}")
    exit(1)

# Test 4: Test caching (generate again)
print("\n4️⃣ Testing cache (generating again)...")

try:
    start_time = time.time()
    response = requests.post(
        f'{API_BASE}/ai-generate-path',
        json={'userId': user_id},
        timeout=10
    )
    elapsed = time.time() - start_time
    
    print(f"⏱️  Request took {elapsed:.2f} seconds")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('from_cache'):
            print(f"✅ Cache is working! Response was instant.")
        else:
            print(f"⚠️  Not from cache (might be expected if cache failed)")
    else:
        print(f"⚠️  Cache test failed: {response.status_code}")
        
except Exception as e:
    print(f"⚠️  Cache test error: {e}")

print(f"\n{'=' * 80}")
print("🎉 All tests completed!")
print("=" * 80)
