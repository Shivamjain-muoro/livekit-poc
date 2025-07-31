"""
Database Viewer for Interview System
"""

import sqlite3
import json

def view_database():
    print("🗄️ Interview Database Viewer")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('interview_sessions.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📊 Tables: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        print("\n👤 CANDIDATE PROFILES:")
        print("-" * 30)
        cursor.execute("SELECT * FROM candidate_profiles")
        profiles = cursor.fetchall()
        for profile in profiles:
            print(f"   Session: {profile[0]}")
            print(f"   Name: {profile[1]}")
            print(f"   Position: {profile[2]}")
            print(f"   Skills: {profile[4]}")
            print()
        
        print("💬 INTERVIEW RESPONSES:")
        print("-" * 30)
        cursor.execute("SELECT session_id, question, response, evaluation FROM interview_responses")
        responses = cursor.fetchall()
        for i, (session_id, question, response, evaluation) in enumerate(responses, 1):
            print(f"   Response #{i} (Session: {session_id})")
            print(f"   Q: {question[:80]}...")
            print(f"   A: {response[:80]}...")
            print(f"   Eval: {evaluation[:50]}...")
            print()
        
        print("🎯 COMPLETED SESSIONS:")
        print("-" * 30)
        cursor.execute("SELECT * FROM interview_sessions")
        sessions = cursor.fetchall()
        for session in sessions:
            print(f"   Session: {session[0]}")
            print(f"   Status: {session[2]}")
            print(f"   Responses: {session[4]}")
            print(f"   Assessment: {session[1][:100]}...")
            print()
        
        conn.close()
        
        print("✅ Database viewer completed!")
        
    except Exception as e:
        print(f"❌ Error viewing database: {e}")

if __name__ == "__main__":
    view_database()
