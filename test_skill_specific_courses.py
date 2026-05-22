"""
Test script to verify skill-specific course generation
"""

import sys
sys.path.insert(0, '.')

from ai_generator import create_fallback_learning_path

# Test with multiple different skills
test_skills = [
    {'name': 'React', 'level': 3},
    {'name': 'Python', 'level': 2},
    {'name': 'Node.js', 'level': 2},
    {'name': 'SQL', 'level': 1},
    {'name': 'Docker', 'level': 1}
]

test_skill_gaps = [
    {'name': 'React', 'level': 3},
    {'name': 'Python', 'level': 2}
]

print("=" * 80)
print("🧪 Testing Skill-Specific Course Generation")
print("=" * 80)

print("\n📊 Input Skills:")
for skill in test_skills:
    level_name = ['Beginner', 'Novice', 'Intermediate', 'Advanced', 'Expert'][skill['level'] - 1]
    print(f"  - {skill['name']}: Level {skill['level']} ({level_name})")

print("\n🚀 Generating fallback learning path...")
result = create_fallback_learning_path('web-development', 'intermediate', test_skills, test_skill_gaps)

print("\n✅ Generated Skills:")
for skill in result['skills']:
    print(f"  - {skill['name']}: {skill['level']} (Priority: {skill['priority']})")

print("\n📚 Generated Courses:")
for i, course in enumerate(result['courses'], 1):
    print(f"\n{i}. {course['title']}")
    print(f"   Provider: {course['provider']}")
    print(f"   Level: {course['level']}")
    print(f"   Duration: {course['duration']}")
    print(f"   Skills Covered: {', '.join(course['skills_covered'])}")
    print(f"   URL: {course['url']}")

print("\n" + "=" * 80)
print("✅ Test Complete!")
print("=" * 80)

# Verify each skill has a unique course
print("\n🔍 Verification:")
skill_names = [s['name'] for s in test_skills]
course_titles = [c['title'] for c in result['courses']]

print(f"  - Total skills: {len(skill_names)}")
print(f"  - Total courses: {len(course_titles)}")
print(f"  - Unique course titles: {len(set(course_titles))}")

# Check if each skill is covered
covered_skills = set()
for course in result['courses']:
    covered_skills.update(course['skills_covered'])

print(f"  - Skills covered in courses: {len(covered_skills)}")

if len(set(course_titles)) == len(course_titles):
    print("\n✅ SUCCESS: All courses have unique titles!")
else:
    print("\n❌ FAIL: Some courses have duplicate titles!")

if len(covered_skills) >= len(skill_names):
    print("✅ SUCCESS: All skills are covered!")
else:
    print(f"⚠️  WARNING: Only {len(covered_skills)}/{len(skill_names)} skills covered")

print("\n" + "=" * 80)
