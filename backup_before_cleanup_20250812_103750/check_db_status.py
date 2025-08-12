"""
Direct Database Check - Current Status
"""

import sqlite3
import os
from datetime import datetime

def check_database_status():
    print("🔍 DIRECT DATABASE STATUS CHECK")
    print("=" * 50)
    
    # Check if database directory exists
    if not os.path.exists("database"):
        print("❌ Database directory not found")
        return
    
    # Check database files
    db_new = os.path.join("database", "interview_evaluations.db")
    db_old = os.path.join("database", "interview_sessions.db")
    
    print("📁 Database Files:")
    for db_path, name in [(db_new, "NEW"), (db_old, "OLD")]:
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(db_path))
            print(f"   ✅ {name}: {db_path} - {size} bytes - Modified: {mod_time}")
        else:
            print(f"   ❌ {name}: Not found")
    
    # Check new database content
    if os.path.exists(db_new):
        print(f"\n📊 INTERVIEW_EVALUATIONS.DB CONTENT:")
        try:
            with sqlite3.connect(db_new) as conn:
                # Check tables
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"   Tables: {tables}")
                
                # Check sessions
                if "interview_sessions" in tables:
                    cursor = conn.execute("SELECT COUNT(*) FROM interview_sessions")
                    count = cursor.fetchone()[0]
                    print(f"   Total sessions: {count}")
                    
                    # Get recent sessions
                    cursor = conn.execute("""
                        SELECT session_id, candidate_name, start_time, overall_score, status
                        FROM interview_sessions 
                        ORDER BY start_time DESC LIMIT 5
                    """)
                    sessions = cursor.fetchall()
                    
                    print(f"   Recent sessions:")
                    for i, session in enumerate(sessions):
                        session_id, name, start_time, score, status = session
                        print(f"     {i+1}. {session_id} | {name} | {start_time} | Score: {score or 0} | {status}")
                        
                        # Check for exchanges
                        if "interview_exchanges" in tables:
                            ex_cursor = conn.execute("SELECT COUNT(*) FROM interview_exchanges WHERE session_id = ?", (session_id,))
                            ex_count = ex_cursor.fetchone()[0]
                            print(f"        📝 Exchanges: {ex_count}")
                
        except Exception as e:
            print(f"   ❌ Error reading database: {e}")
    
    # Check if agent left any logs
    print(f"\n🔍 LOOKING FOR AGENT ACTIVITY:")
    if os.path.exists("agent.log"):
        print("   ✅ Agent log file found")
        with open("agent.log", "r") as f:
            lines = f.readlines()
            print(f"   📝 Log lines: {len(lines)}")
            if lines:
                print(f"   Last log: {lines[-1].strip()}")
    else:
        print("   ❌ No agent log file found")
    
    # Check for recent Python processes
    print(f"\n🔍 CHECKING FOR RECENT ACTIVITY:")
    try:
        import subprocess
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        if 'python.exe' in result.stdout:
            print("   ✅ Python processes currently running")
        else:
            print("   ❌ No Python processes found")
    except:
        print("   ❓ Could not check processes")

if __name__ == "__main__":
    check_database_status()
