#!/usr/bin/env python3
"""
Simple script to view interview database contents with proper error handling
"""

def get_db_path():
    """Get the correct database path"""
    import os
    db_path = os.path.join('database', 'interview_sessions.db')
    if not os.path.exists(db_path):
        db_path = 'interview_sessions.db'  # Fallback
    return db_path

import sqlite3
import json

def view_interview_data():
    print("📋 INTERVIEW DATABASE CONTENTS")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Get all sessions
        cursor.execute("""
            SELECT session_id, name, position, experience_level, skills, created_at
            FROM candidate_profiles 
            ORDER BY created_at DESC
        """)
        
        profiles = cursor.fetchall()
        
        for profile in profiles:
            session_id = profile[0]
            print(f"\n🎯 SESSION: {session_id}")
            print("=" * 60)
            
            print("👤 CANDIDATE PROFILE:")
            print(f"   Name: {profile[1]}")
            print(f"   Position: {profile[2]}")
            print(f"   Experience: {profile[3]}")
            print(f"   Skills: {profile[4]}")
            print(f"   Created: {profile[5]}")
            
            # Get session completion status
            cursor.execute("SELECT overall_assessment, status, completed_at, total_responses FROM interview_sessions WHERE session_id = ?", (session_id,))
            session_data = cursor.fetchone()
            
            if session_data:
                print(f"\n📊 INTERVIEW STATUS:")
                print(f"   Status: {session_data[1]}")
                print(f"   Completed: {session_data[2]}")
                print(f"   Total Responses: {session_data[3]}")
                print(f"   Overall Assessment:")
                print(f"   {session_data[0]}")
            
            # Get all responses
            cursor.execute("""
                SELECT question, response, evaluation, timestamp 
                FROM interview_responses 
                WHERE session_id = ? 
                ORDER BY timestamp
            """, (session_id,))
            
            responses = cursor.fetchall()
            
            print(f"\n💬 INTERVIEW RESPONSES ({len(responses)} total):")
            
            for i, (question, response, evaluation, timestamp) in enumerate(responses, 1):
                print(f"\n   --- RESPONSE {i} ---")
                print(f"   Time: {timestamp}")
                print(f"   Question: {question}")
                print(f"   \n   Candidate Answer:")
                print(f"   {response}")
                print(f"   \n   Evaluation:")
                print(f"   {evaluation}")
                print(f"   {'-' * 50}")
            
            print("\n" + "=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    view_interview_data()
