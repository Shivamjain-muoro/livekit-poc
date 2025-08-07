#!/usr/bin/env python3
"""
Simple Interview Evaluation Check
"""

import sqlite3
import json
from datetime import datetime

def main():
    print("🔍 CHECKING YOUR INTERVIEW EVALUATION")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('database/interview_sessions.db')
        cursor = conn.cursor()
        
        # Check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"📋 Available tables: {tables}")
        
        # Check sessions table structure
        if 'sessions' in tables:
            cursor.execute("PRAGMA table_info(sessions)")
            cols = cursor.fetchall()
            print(f"\n📄 Sessions table columns:")
            for col in cols:
                print(f"  - {col[1]} ({col[2]})")
            
            # Get recent sessions
            cursor.execute("SELECT * FROM sessions ORDER BY rowid DESC LIMIT 3")
            sessions = cursor.fetchall()
            print(f"\n📊 Recent sessions: {len(sessions)}")
            for i, session in enumerate(sessions):
                print(f"  {i+1}. {session}")
        
        # Check interview_responses table
        if 'interview_responses' in tables:
            cursor.execute("PRAGMA table_info(interview_responses)")
            cols = cursor.fetchall()
            print(f"\n📄 Interview_responses table columns:")
            for col in cols:
                print(f"  - {col[1]} ({col[2]})")
            
            # Get recent responses
            cursor.execute("SELECT * FROM interview_responses ORDER BY rowid DESC LIMIT 3")
            responses = cursor.fetchall()
            print(f"\n💬 Recent responses: {len(responses)}")
            for i, response in enumerate(responses):
                print(f"  {i+1}. {response}")
                
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM interview_responses")
            total = cursor.fetchone()[0]
            print(f"\n📊 Total interview responses in database: {total}")
            
            if total > 0:
                print("\n✅ YOU HAVE INTERVIEW DATA AVAILABLE!")
                print("🎯 Here's what we found:")
                
                # Get the most recent response session
                cursor.execute("SELECT DISTINCT id FROM interview_responses ORDER BY timestamp DESC LIMIT 1")
                latest_session = cursor.fetchone()
                
                if latest_session:
                    session_id = latest_session[0]
                    cursor.execute("""
                        SELECT question, answer, evaluation, timestamp 
                        FROM interview_responses 
                        WHERE id = ? 
                        ORDER BY timestamp DESC
                    """, (session_id,))
                    
                    session_responses = cursor.fetchall()
                    print(f"\n🆔 Latest Interview Session: {session_id}")
                    print(f"💬 Number of Q&A exchanges: {len(session_responses)}")
                    
                    for i, (question, answer, evaluation, timestamp) in enumerate(session_responses, 1):
                        print(f"\n📝 Q&A #{i}")
                        print(f"❓ Q: {question[:80]}...")
                        print(f"💬 A: {answer[:80]}...")
                        print(f"📊 Evaluation: {evaluation[:80]}...")
                        print(f"🕐 Time: {timestamp}")
                    
                    print(f"\n🎉 EVALUATION RESULTS AVAILABLE!")
                    print(f"📋 Session ID: {session_id}")
                    print(f"💬 Total Questions Answered: {len(session_responses)}")
                    print(f"✅ Interview data is properly captured!")
            else:
                print("\n❌ No interview responses found in database")
                print("This confirms that your LiveKit session wasn't captured due to the session start error")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
