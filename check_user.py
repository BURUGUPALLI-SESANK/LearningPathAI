import sqlite3

conn = sqlite3.connect('data/users.db')
cursor = conn.cursor()

user_email = 'bsesankbsesank@gmail.com'

print(f"\n{'='*60}")
print(f"DATABASE CHECK FOR: {user_email}")
print(f"{'='*60}\n")

# Check profile
cursor.execute('SELECT user_id, email, full_name FROM users WHERE user_id=?', (user_email,))
user = cursor.fetchone()
if user:
    print("✅ PROFILE SAVED:")
    print(f"   User ID: {user[0]}")
    print(f"   Email: {user[1]}")
    print(f"   Name: {user[2]}")
else:
    print("❌ Profile: NOT FOUND")

print()

# Check assessment
cursor.execute('SELECT COUNT(*) FROM assessments WHERE user_id=?', (user_email,))
assessment_count = cursor.fetchone()[0]
if assessment_count > 0:
    print(f"✅ ASSESSMENT SAVED: {assessment_count} assessment(s)")
else:
    print("❌ Assessment: NOT SAVED")

print()

# Check learning path
cursor.execute('SELECT ai_generated, created_at FROM learning_paths WHERE user_id=? ORDER BY created_at DESC LIMIT 1', (user_email,))
lp = cursor.fetchone()
if lp:
    print(f"✅ LEARNING PATH SAVED:")
    print(f"   AI Generated: {'Yes' if lp[0] else 'No'}")
    print(f"   Created: {lp[1]}")
else:
    print("❌ Learning Path: NOT SAVED")

print()

# Check daily tasks
cursor.execute('SELECT progress, completed_tasks, total_tasks, updated_at FROM daily_tasks WHERE user_id=? ORDER BY updated_at DESC LIMIT 1', (user_email,))
dt = cursor.fetchone()
if dt:
    print(f"✅ DAILY TASKS SAVED:")
    print(f"   Progress: {dt[0]}%")
    print(f"   Completed: {dt[1]}/{dt[2]} tasks")
    print(f"   Updated: {dt[3]}")
else:
    print("❌ Daily Tasks: NOT SAVED")

print()

# Check employability
cursor.execute('SELECT COUNT(*) FROM employability WHERE user_id=?', (user_email,))
emp_count = cursor.fetchone()[0]
if emp_count > 0:
    print(f"✅ EMPLOYABILITY SCORE: {emp_count} score(s) saved")
else:
    print("❌ Employability Score: NOT SAVED")

print(f"\n{'='*60}\n")

conn.close()
