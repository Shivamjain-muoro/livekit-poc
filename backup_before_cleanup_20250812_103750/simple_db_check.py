#!/usr/bin/env python3
"""
Simple Database Check for Interview Data
"""

import sqlite3
import json
from datetime import datetime

def check_db():
    try:
        conn = sqlite3.connect('database/interview_sessions.db')
        cursor = conn.cursor()
        
        print("🔍 CHECKING DATABASE FOR YOUR INTERVIEW")
        print("=" * 50)
        
        # Check sessions table
        cursor.execute("SELECT COUNT(*) FROM sessions")
        session_count = cursor.fetchone()[0]
        print(f"📊 Total sessions: {session_count}")
        
        if session_count > 0:
            # Get recent sessions
            cursor.execute("SELECT * FROM sessions ORDER BY rowid DESC LIMIT 5")
            sessions = cursor.fetchall()
            
            print(f"\n📋 Recent Sessions:")
            for i, session in enumerate(sessions):
                print(f"  {i+1}. {session}")
            
            # Check for today's sessions
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT * FROM sessions WHERE date(start_time) = ?", (today,))
            today_sessions = cursor.fetchall()
            
            print(f"\n📅 Today's Sessions ({today}): {len(today_sessions)}")
            for session in today_sessions:
                print(f"  📋 {session}")
        
        # Check interview_responses table
        cursor.execute("SELECT COUNT(*) FROM interview_responses")
        response_count = cursor.fetchone()[0]
        print(f"\n💬 Total responses: {response_count}")
        
        if response_count > 0:
            cursor.execute("SELECT * FROM interview_responses ORDER BY rowid DESC LIMIT 3")
            responses = cursor.fetchall()
            print(f"📝 Recent responses:")
            for response in responses:
                print(f"  {response}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_db()
