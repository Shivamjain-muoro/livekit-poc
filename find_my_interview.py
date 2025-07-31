#!/usr/bin/env python3

import sqlite3
from datetime import datetime

def find_my_recent_interview():
    """Find your most recent interview sessions"""
    
    conn = sqlite3.connect('interview_sessions.db')
    cursor = conn.cursor()
    
    print("🔍 SEARCHING FOR YOUR RECENT INTERVIEWS")
    print("=" * 50)
    
    # Check today's sessions
    print("\n📅 TODAY'S SESSIONS (July 31, 2025):")
    cursor.execute("SELECT * FROM sessions WHERE created_at LIKE '2025-07-31%' ORDER BY created_at DESC")
    today_sessions = cursor.fetchall()
    
    if today_sessions:
        for i, session in enumerate(today_sessions, 1):
            print(f"  {i}. {session[1]} ({session[2]}) - {session[5]} - {session[14]}")
    else:
        print("  ❌ No sessions found for today")
    
    # Check your email sessions
    print(f"\n📧 YOUR EMAIL SESSIONS (shivamj075@gmail.com):")
    cursor.execute("SELECT * FROM sessions WHERE participant_email = 'shivamj075@gmail.com' ORDER BY created_at DESC LIMIT 5")
    your_sessions = cursor.fetchall()
    
    if your_sessions:
        for i, session in enumerate(your_sessions, 1):
            session_id, name, email, position, exp_level, status, room_name, current_q, total_q, start_time, end_time, pause_duration, interview_data, skills, created_at, updated_at = session
            print(f"\n  📋 SESSION {i}: {name}")
            print(f"     🆔 ID: {session_id}")
            print(f"     💼 Position: {position}")
            print(f"     🔄 Status: {status}")
            print(f"     ⏰ Created: {created_at}")
            print(f"     📈 Progress: {current_q}/{total_q} questions")
            if start_time:
                print(f"     🎯 Started: {start_time}")
            if end_time:
                print(f"     ✅ Ended: {end_time}")
            
            # Check if there are any responses for this session
            cursor.execute("SELECT COUNT(*) FROM answers WHERE session_id = ?", (session_id,))
            answer_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM feedback WHERE session_id = ?", (session_id,))
            feedback_count = cursor.fetchone()[0]
            
            print(f"     💬 Responses: {answer_count}")
            print(f"     ⭐ Evaluations: {feedback_count}")
    else:
        print("  ❌ No sessions found for your email")
    
    # Check for any completed sessions
    print(f"\n✅ COMPLETED SESSIONS (All users):")
    cursor.execute("SELECT * FROM sessions WHERE status = 'completed' ORDER BY created_at DESC LIMIT 5")
    completed_sessions = cursor.fetchall()
    
    if completed_sessions:
        for i, session in enumerate(completed_sessions, 1):
            print(f"  {i}. {session[1]} ({session[2]}) - {session[3]} - {session[14]}")
    else:
        print("  ❌ No completed sessions found")
    
    # Check the most recent activity overall
    print(f"\n🕐 MOST RECENT ACTIVITY:")
    cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC LIMIT 1")
    latest_session = cursor.fetchone()
    
    if latest_session:
        print(f"  Latest session: {latest_session[1]} - {latest_session[14]}")
        
        # Check for latest answer
        cursor.execute("SELECT submitted_at FROM answers ORDER BY submitted_at DESC LIMIT 1")
        latest_answer = cursor.fetchone()
        if latest_answer:
            print(f"  Latest answer: {latest_answer[0]}")
        
        # Check for latest feedback
        cursor.execute("SELECT evaluated_at FROM feedback ORDER BY evaluated_at DESC LIMIT 1")
        latest_feedback = cursor.fetchone()
        if latest_feedback:
            print(f"  Latest feedback: {latest_feedback[0]}")
    
    conn.close()

if __name__ == "__main__":
    find_my_recent_interview()
