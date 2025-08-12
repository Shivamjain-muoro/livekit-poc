"""
Search for Real Interview Session
Find the actual interview session from the LiveKit room
"""

import sqlite3
import os
import json
from datetime import datetime

def search_real_interview():
    """Search for the real interview session"""
    print("🔍 SEARCHING FOR REAL INTERVIEW SESSION")
    print("=" * 50)
    
    # Your room details from the URL
    room_name = "interview_eac86959"
    
    # Check both databases
    db_new = os.path.join("database", "interview_evaluations.db")
    db_old = os.path.join("database", "interview_sessions.db")
    
    print(f"🎯 Looking for room: {room_name}")
    print(f"🗄️ Database 1: {db_new} - Size: {os.path.getsize(db_new)} bytes")
    print(f"🗄️ Database 2: {db_old} - Size: {os.path.getsize(db_old)} bytes")
    
    # Search new database
    print("\n📊 SEARCHING INTERVIEW_EVALUATIONS.DB:")
    if os.path.exists(db_new):
        with sqlite3.connect(db_new) as conn:
            # Get all sessions
            cursor = conn.execute("""
                SELECT session_id, candidate_name, position, start_time, status, overall_score
                FROM interview_sessions ORDER BY start_time DESC
            """)
            sessions = cursor.fetchall()
            
            print(f"Total sessions: {len(sessions)}")
            
            found_real = False
            for i, session in enumerate(sessions):
                session_id, name, position, start_time, status, score = session
                print(f"\n{i+1}. Session: {session_id}")
                print(f"   Name: {name}")
                print(f"   Position: {position}")
                print(f"   Start: {start_time}")
                print(f"   Status: {status}")
                print(f"   Score: {score or 0}")
                
                # Check if this matches your room
                if room_name in session_id or "eac86959" in session_id:
                    print("   ✅ THIS IS YOUR REAL SESSION!")
                    found_real = True
                    
                    # Get exchanges for this session
                    exchanges_cursor = conn.execute("""
                        SELECT question, response, ai_evaluation, relevance_score
                        FROM interview_exchanges WHERE session_id = ?
                    """, (session_id,))
                    exchanges = exchanges_cursor.fetchall()
                    print(f"   📝 Exchanges: {len(exchanges)}")
                    
                    for j, exchange in enumerate(exchanges[:3]):  # Show first 3
                        print(f"      Q{j+1}: {exchange[0][:50]}...")
                        print(f"      A{j+1}: {exchange[1][:50]}...")
                        print(f"      Score: {exchange[3] or 0}")
            
            if not found_real:
                print("❌ Your real session not found in new database")
    
    # Search old database
    print("\n📊 SEARCHING INTERVIEW_SESSIONS.DB:")
    if os.path.exists(db_old):
        with sqlite3.connect(db_old) as conn:
            # Check tables
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"Tables: {tables}")
            
            if "interview_sessions" in tables:
                # Get sessions from old database
                cursor = conn.execute("SELECT * FROM interview_sessions ORDER BY start_time DESC")
                sessions = cursor.fetchall()
                print(f"Sessions in old DB: {len(sessions)}")
                
                for session in sessions:
                    if len(session) > 0:
                        session_id = session[0]
                        print(f"Old session: {session_id}")
                        if room_name in session_id or "eac86959" in session_id:
                            print("   ✅ FOUND YOUR SESSION IN OLD DB!")
                            print(f"   Full data: {session}")
    
    # Also check if the agent is running and created a session
    print("\n🔍 CHECKING FOR AGENT ACTIVITY:")
    
    # Look for any recent activity
    if os.path.exists(db_new):
        with sqlite3.connect(db_new) as conn:
            cursor = conn.execute("""
                SELECT session_id, start_time FROM interview_sessions 
                WHERE start_time > '2025-08-06' ORDER BY start_time DESC
            """)
            recent_sessions = cursor.fetchall()
            
            print(f"Sessions today (2025-08-06): {len(recent_sessions)}")
            for session_id, start_time in recent_sessions:
                print(f"  - {session_id} at {start_time}")

if __name__ == "__main__":
    search_real_interview()
