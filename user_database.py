"""
User Database Management with SQLite
Maintains consistency of all user data per account
"""

import sqlite3
import json
from datetime import datetime
import os

DB_PATH = 'data/users.db'

def init_user_database():
    """Initialize SQLite database for user data"""
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            full_name TEXT,
            profile_data TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    # Assessments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            assessment_data TEXT,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Learning paths table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            path_data TEXT,
            ai_generated BOOLEAN,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            progress_data TEXT,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Employability scores table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            score_data TEXT,
            calculated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Daily tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            tasks_data TEXT,
            progress INTEGER,
            completed_tasks INTEGER,
            total_tasks INTEGER,
            updated_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ User database initialized")


# User operations
def save_user(user_id, email, full_name, profile_data):
    """Save or update user profile"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, email, full_name, profile_data, created_at, updated_at)
        VALUES (?, ?, ?, ?, COALESCE((SELECT created_at FROM users WHERE user_id = ?), ?), ?)
    ''', (user_id, email, full_name, json.dumps(profile_data), user_id, now, now))
    
    conn.commit()
    conn.close()
    print(f"✅ Saved user: {user_id}")


def get_user(user_id):
    """Get user profile"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT profile_data FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None


# Assessment operations
def save_assessment(user_id, assessment_data):
    """Save user assessment"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Delete old assessments for this user
    cursor.execute('DELETE FROM assessments WHERE user_id = ?', (user_id,))
    
    # Insert new assessment
    cursor.execute('''
        INSERT INTO assessments (user_id, assessment_data, created_at)
        VALUES (?, ?, ?)
    ''', (user_id, json.dumps(assessment_data), datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    print(f"✅ Saved assessment for user: {user_id}")


def get_assessment(user_id):
    """Get user assessment"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT assessment_data FROM assessments 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None


# Learning path operations
def save_learning_path(user_id, path_data, ai_generated=False):
    """Save learning path for user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Delete old paths for this user
    cursor.execute('DELETE FROM learning_paths WHERE user_id = ?', (user_id,))
    
    # Insert new path
    cursor.execute('''
        INSERT INTO learning_paths (user_id, path_data, ai_generated, created_at)
        VALUES (?, ?, ?, ?)
    ''', (user_id, json.dumps(path_data), ai_generated, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    print(f"✅ Saved learning path for user: {user_id} (AI: {ai_generated})")


def get_learning_path(user_id):
    """Get user's learning path"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT path_data, ai_generated, created_at FROM learning_paths 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'path': json.loads(result[0]),
            'ai_generated': bool(result[1]),
            'created_at': result[2]
        }
    return None


# Progress operations
def save_progress(user_id, progress_data):
    """Save user progress"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Delete old progress
    cursor.execute('DELETE FROM progress WHERE user_id = ?', (user_id,))
    
    # Insert new progress
    cursor.execute('''
        INSERT INTO progress (user_id, progress_data, updated_at)
        VALUES (?, ?, ?)
    ''', (user_id, json.dumps(progress_data), datetime.now().isoformat()))
    
    conn.commit()
    conn.close()


def get_progress(user_id):
    """Get user progress"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT progress_data FROM progress 
        WHERE user_id = ? 
        ORDER BY updated_at DESC 
        LIMIT 1
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None


# Employability operations
def save_employability(user_id, score_data):
    """Save employability score"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO employability (user_id, score_data, calculated_at)
        VALUES (?, ?, ?)
    ''', (user_id, json.dumps(score_data), datetime.now().isoformat()))
    
    conn.commit()
    conn.close()


def get_employability(user_id):
    """Get latest employability score"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT score_data FROM employability 
        WHERE user_id = ? 
        ORDER BY calculated_at DESC 
        LIMIT 1
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None


# Daily tasks operations
def save_daily_tasks(user_id, tasks_data, progress, completed, total):
    """Save daily tasks for user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Delete old tasks
    cursor.execute('DELETE FROM daily_tasks WHERE user_id = ?', (user_id,))
    
    # Insert new tasks
    cursor.execute('''
        INSERT INTO daily_tasks (user_id, tasks_data, progress, completed_tasks, total_tasks, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, json.dumps(tasks_data), progress, completed, total, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    print(f"✅ Saved daily tasks for user: {user_id}")


def get_daily_tasks(user_id):
    """Get user's daily tasks"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT tasks_data, progress, completed_tasks, total_tasks, updated_at 
        FROM daily_tasks 
        WHERE user_id = ? 
        ORDER BY updated_at DESC 
        LIMIT 1
    ''', (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'tasks': json.loads(result[0]),
            'progress': result[1],
            'completed': result[2],
            'total': result[3],
            'updated_at': result[4]
        }
    return None


# Initialize database on import
init_user_database()
