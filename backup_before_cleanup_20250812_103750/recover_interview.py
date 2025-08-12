"""
Manual Interview Session Recovery
Add your recent interview session to the database
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta

def recover_recent_interview():
    """Manually add the recent interview session based on agent logs"""
    print("🔄 RECOVERING YOUR RECENT INTERVIEW SESSION")
    print("=" * 50)
    
    # Based on your logs, your interview details:
    room_name = "interview_9fd6d9ec"
    session_id = room_name
    candidate_name = "Interview Candidate"  # From logs
    position = "Applied Position"
    
    # Estimate timing from logs (17:16 - 17:19)
    start_time = "2025-08-06 17:16:40"  # From log: "received job request"
    end_time = "2025-08-06 17:19:00"    # From log: "participant disconnect"
    
    print(f"📋 Recovering session:")
    print(f"   🆔 Session ID: {session_id}")
    print(f"   👤 Candidate: {candidate_name}")
    print(f"   💼 Position: {position}")
    print(f"   🕐 Start: {start_time}")
    print(f"   🕑 End: {end_time}")
    
    # Connect to database
    db_path = os.path.join("database", "interview_evaluations.db")
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Check if session already exists
            cursor = conn.execute("""
                SELECT session_id FROM interview_sessions WHERE session_id = ?
            """, (session_id,))
            
            if cursor.fetchone():
                print(f"✅ Session {session_id} already exists in database!")
                return session_id
            
            # Insert the session
            conn.execute("""
                INSERT INTO interview_sessions 
                (session_id, candidate_name, position, start_time, end_time, status, overall_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                candidate_name,
                position,
                start_time,
                end_time,
                "completed",
                0  # Will be calculated later
            ))
            
            # Add a recovery note as an exchange
            conn.execute("""
                INSERT INTO interview_exchanges 
                (session_id, question, response, timestamp, ai_evaluation)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                "Interview Recovery Note",
                "This interview session was recovered from agent logs. The interview took place on 2025-08-06 from 17:16 to 17:19. The agent was running and participant was connected, but data wasn't captured due to tool configuration issues.",
                start_time,
                "Session recovered: Agent detected participant 'Interview Candidate' in room 'interview_9fd6d9ec'. Interview duration approximately 3 minutes. Tools were executed but data storage was incomplete."
            ))
            
            conn.commit()
            print("✅ Session successfully added to database!")
            
            # Verify
            cursor = conn.execute("""
                SELECT session_id, candidate_name, start_time, end_time
                FROM interview_sessions WHERE session_id = ?
            """, (session_id,))
            
            result = cursor.fetchone()
            if result:
                print(f"✅ Verification: {result}")
                return session_id
            else:
                print("❌ Verification failed")
                return None
                
    except Exception as e:
        print(f"❌ Error recovering session: {e}")
        return None

def check_recovered_session(session_id):
    """Check the recovered session"""
    print(f"\n📊 CHECKING RECOVERED SESSION: {session_id}")
    print("=" * 40)
    
    db_path = os.path.join("database", "interview_evaluations.db")
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Get session details
            cursor = conn.execute("""
                SELECT session_id, candidate_name, position, start_time, end_time, status, overall_score
                FROM interview_sessions WHERE session_id = ?
            """, (session_id,))
            
            session = cursor.fetchone()
            if session:
                print(f"📋 Session: {session[0]}")
                print(f"👤 Candidate: {session[1]}")
                print(f"💼 Position: {session[2]}")
                print(f"🕐 Start: {session[3]}")
                print(f"🕑 End: {session[4]}")
                print(f"📋 Status: {session[5]}")
                print(f"📊 Score: {session[6]}")
                
                # Get exchanges
                cursor = conn.execute("""
                    SELECT question, response, ai_evaluation
                    FROM interview_exchanges WHERE session_id = ?
                """, (session_id,))
                
                exchanges = cursor.fetchall()
                print(f"\n💬 Exchanges: {len(exchanges)}")
                
                for i, exchange in enumerate(exchanges):
                    print(f"\n   {i+1}. Q: {exchange[0]}")
                    print(f"      A: {exchange[1][:100]}...")
                    print(f"      Eval: {exchange[2][:100]}...")
                
                return True
            else:
                print("❌ Session not found")
                return False
                
    except Exception as e:
        print(f"❌ Error checking session: {e}")
        return False

def main():
    print("🎙️ INTERVIEW SESSION RECOVERY TOOL")
    print("=" * 50)
    print("This will add your recent interview session to the database")
    print("based on the agent logs you provided.")
    
    proceed = input("\nProceed with recovery? (y/n): ").strip().lower()
    
    if proceed != 'y':
        print("Recovery cancelled.")
        return
    
    # Recover the session
    session_id = recover_recent_interview()
    
    if session_id:
        print(f"\n✅ SUCCESS! Your interview session has been recovered.")
        
        # Check the recovered session
        check_recovered_session(session_id)
        
        print(f"\n🎯 NEXT STEPS:")
        print("1. Run 'python view_interview_reports.py' to see your session")
        print("2. The session is marked as completed but has limited data")
        print("3. For future interviews, the fixed tools will capture everything")
        print("4. Your interview system is now properly configured!")
        
    else:
        print("\n❌ Recovery failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
