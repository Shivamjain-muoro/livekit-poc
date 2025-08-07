#!/usr/bin/env python3
"""
Check Interview Data - Find and analyze captured interview data
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta

def check_interview_data():
    """Check all possible locations for interview data"""
    print("🔍 COMPREHENSIVE INTERVIEW DATA CHECK")
    print("=" * 50)
    
    # Check database
    db_path = "database/interview_sessions.db"
    if os.path.exists(db_path):
        print(f"✅ Database found: {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in cursor.fetchall()]
            print(f"📋 Tables: {tables}")
            
            if 'sessions' in tables:
                # Check total sessions
                cursor.execute('SELECT COUNT(*) FROM sessions')
                total_sessions = cursor.fetchone()[0]
                print(f"📊 Total sessions: {total_sessions}")
                
                # Check recent sessions (last 4 hours)
                four_hours_ago = (datetime.now() - timedelta(hours=4)).isoformat()
                cursor.execute('''
                    SELECT session_id, candidate_name, start_time, end_time, status,
                           (SELECT COUNT(*) FROM qa_exchanges WHERE session_id = s.session_id) as exchanges
                    FROM sessions s 
                    WHERE start_time > ? 
                    ORDER BY start_time DESC
                ''', (four_hours_ago,))
                
                recent_sessions = cursor.fetchall()
                print(f"🕐 Recent sessions (4 hours): {len(recent_sessions)}")
                
                for session in recent_sessions:
                    print(f"\n  🆔 Session: {session[0]}")
                    print(f"  👤 Candidate: {session[1]}")
                    print(f"  📅 Start: {session[2]}")
                    print(f"  📅 End: {session[3] if session[3] else 'ongoing'}")
                    print(f"  📊 Status: {session[4]}")
                    print(f"  💬 Exchanges: {session[5]}")
                
                # Check for any session that might match our LiveKit room
                cursor.execute('''
                    SELECT * FROM sessions 
                    WHERE session_id LIKE '%6c6757d6%' 
                       OR session_id = 'interview_6c6757d6'
                       OR candidate_name LIKE '%candidate%'
                    ORDER BY start_time DESC
                ''')
                
                matching_sessions = cursor.fetchall()
                if matching_sessions:
                    print(f"\n🎯 Potential LiveKit sessions found: {len(matching_sessions)}")
                    for session in matching_sessions:
                        print(f"  📋 {session}")
                else:
                    print("\n❌ No LiveKit session found in database")
                
                # Check all sessions from today
                today = datetime.now().strftime('%Y-%m-%d')
                cursor.execute('''
                    SELECT session_id, candidate_name, start_time, status,
                           (SELECT COUNT(*) FROM qa_exchanges WHERE session_id = s.session_id) as exchanges
                    FROM sessions s 
                    WHERE date(start_time) = ? 
                    ORDER BY start_time DESC
                ''', (today,))
                
                today_sessions = cursor.fetchall()
                print(f"\n📅 All sessions today ({today}): {len(today_sessions)}")
                for session in today_sessions:
                    print(f"  🆔 {session[0]} | 👤 {session[1]} | 📅 {session[2]} | 📊 {session[3]} | 💬 {session[4]}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Database error: {e}")
    else:
        print(f"❌ Database not found: {db_path}")
    
    # Check log files
    print(f"\n🔍 CHECKING LOG FILES")
    print("=" * 30)
    
    log_files = [
        "interview_detailed.log",
        "interview.log",
        "agent.log"
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"✅ Found log: {log_file}")
            
            # Check for recent entries
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    print(f"  📄 Total lines: {len(lines)}")
                    
                    # Show last 5 lines
                    if lines:
                        print("  📝 Last 5 entries:")
                        for line in lines[-5:]:
                            print(f"    {line.strip()}")
            except Exception as e:
                print(f"  ❌ Error reading {log_file}: {e}")
        else:
            print(f"❌ Log not found: {log_file}")
    
    # Check for any potential data files
    print(f"\n🔍 CHECKING FOR DATA FILES")
    print("=" * 30)
    
    import glob
    data_patterns = [
        "*.json",
        "interview_*.txt",
        "session_*.json",
        "**/*.db"
    ]
    
    for pattern in data_patterns:
        files = glob.glob(pattern, recursive=True)
        if files:
            print(f"📁 {pattern}: {files}")
    
    return recent_sessions if 'recent_sessions' in locals() else []

def analyze_logs_for_interview():
    """Analyze logs to understand what happened during the interview"""
    print(f"\n🔍 ANALYZING LOGS FOR INTERVIEW TRACES")
    print("=" * 50)
    
    log_file = "interview_detailed.log"
    if not os.path.exists(log_file):
        print(f"❌ Log file not found: {log_file}")
        return
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        print(f"📄 Total log lines: {len(lines)}")
        
        # Look for key events
        session_events = []
        tool_calls = []
        errors = []
        
        for i, line in enumerate(lines):
            if "interview_6c6757d6" in line.lower():
                session_events.append(f"Line {i+1}: {line.strip()}")
            elif "executing tool" in line.lower():
                tool_calls.append(f"Line {i+1}: {line.strip()}")
            elif "error" in line.lower():
                errors.append(f"Line {i+1}: {line.strip()}")
        
        print(f"\n🎯 LiveKit Session Events: {len(session_events)}")
        for event in session_events:
            print(f"  {event}")
        
        print(f"\n🔧 Tool Calls: {len(tool_calls)}")
        for call in tool_calls[-5:]:  # Show last 5
            print(f"  {call}")
        
        print(f"\n❌ Errors: {len(errors)}")
        for error in errors[-5:]:  # Show last 5
            print(f"  {error}")
            
    except Exception as e:
        print(f"❌ Error analyzing logs: {e}")

if __name__ == "__main__":
    sessions = check_interview_data()
    analyze_logs_for_interview()
    
    print(f"\n🎯 SUMMARY AND RECOMMENDATIONS")
    print("=" * 40)
    
    if sessions:
        print("✅ Found interview sessions in database")
        print("💡 Use the report generator to get evaluation results")
        print("🔧 Command: python report_generator.py")
    else:
        print("❌ No recent interview sessions found in database")
        print("🔍 This suggests the session auto-start failed")
        print("💡 The interview audio/conversation happened but wasn't recorded")
        print("🛠️ Need to fix the AgentSession.room attribute issue")
        
    print(f"\n🔧 TO FIX THE ISSUE:")
    print("1. Fix the AgentSession room attribute error")
    print("2. Re-run the interview to capture data properly")
    print("3. Or manually create a session entry if conversation data exists")
