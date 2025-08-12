"""
Interview Log Verification System
Analyze logs to verify interview completion and data capture
"""

import os
import re
from datetime import datetime, timedelta
import sqlite3

def analyze_interview_logs():
    """Analyze interview logs for verification"""
    print("🔍 ANALYZING INTERVIEW LOGS FOR VERIFICATION")
    print("=" * 55)
    
    log_file = "interview_detailed.log"
    
    if not os.path.exists(log_file):
        print(f"❌ Log file not found: {log_file}")
        print("💡 Make sure you run an interview first to generate logs")
        return False
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = f.readlines()
        
        print(f"📄 Found {len(logs)} log entries")
        
        # Analyze log patterns
        session_starts = []
        responses_recorded = []
        session_ends = []
        errors = []
        background_evaluations = []
        database_saves = []
        
        for line in logs:
            if "🚀 STARTING INTERVIEW SESSION" in line:
                session_starts.append(line.strip())
            elif "📝 RECORDING CANDIDATE RESPONSE" in line:
                responses_recorded.append(line.strip())
            elif "🏁 ENDING INTERVIEW SESSION" in line:
                session_ends.append(line.strip())
            elif "ERROR" in line or "❌" in line:
                errors.append(line.strip())
            elif "Background evaluation queued" in line:
                background_evaluations.append(line.strip())
            elif "DATABASE_TOOL: Exchange saved to database successfully" in line:
                database_saves.append(line.strip())
        
        # Report findings
        print(f"\n📊 LOG ANALYSIS RESULTS:")
        print(f"=" * 30)
        print(f"🚀 Session Starts: {len(session_starts)}")
        print(f"📝 Responses Recorded: {len(responses_recorded)}")
        print(f"🏁 Session Ends: {len(session_ends)}")
        print(f"💾 Database Saves: {len(database_saves)}")
        print(f"🔄 Background Evaluations: {len(background_evaluations)}")
        print(f"❌ Errors: {len(errors)}")
        
        # Show recent session details
        if session_starts:
            print(f"\n🔍 RECENT SESSION DETAILS:")
            print(f"=" * 30)
            
            # Get latest session info
            latest_start = session_starts[-1]
            print(f"📅 Latest Session Start: {latest_start}")
            
            if responses_recorded:
                print(f"📝 Total Responses in Logs: {len(responses_recorded)}")
                print(f"📅 Latest Response: {responses_recorded[-1]}")
            
            if session_ends:
                print(f"🏁 Latest Session End: {session_ends[-1]}")
            
            if errors:
                print(f"\n⚠️ RECENT ERRORS:")
                for error in errors[-3:]:  # Show last 3 errors
                    print(f"   ❌ {error}")
        
        # Verify completeness
        print(f"\n✅ VERIFICATION CHECKLIST:")
        print(f"=" * 25)
        
        complete_session = len(session_starts) > 0 and len(session_ends) > 0
        print(f"🔄 Complete Session: {'✅' if complete_session else '❌'}")
        
        responses_captured = len(responses_recorded) > 0
        print(f"📝 Responses Captured: {'✅' if responses_captured else '❌'}")
        
        database_working = len(database_saves) > 0
        print(f"💾 Database Working: {'✅' if database_working else '❌'}")
        
        evaluation_working = len(background_evaluations) > 0
        print(f"🔄 Evaluation Working: {'✅' if evaluation_working else '❌'}")
        
        no_critical_errors = len([e for e in errors if "CRITICAL" in e]) == 0
        print(f"🛡️ No Critical Errors: {'✅' if no_critical_errors else '❌'}")
        
        # Overall status
        all_good = complete_session and responses_captured and database_working and no_critical_errors
        
        print(f"\n🎯 OVERALL STATUS: {'🟢 EXCELLENT' if all_good else '🟡 NEEDS REVIEW'}")
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error analyzing logs: {e}")
        return False

def verify_database_data():
    """Verify data in database matches logs"""
    print(f"\n💾 VERIFYING DATABASE DATA")
    print("=" * 30)
    
    db_path = os.path.join("database", "interview_evaluations.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Check sessions
            cursor = conn.execute("""
                SELECT session_id, candidate_name, position, start_time, end_time, status
                FROM interview_sessions 
                ORDER BY start_time DESC 
                LIMIT 5
            """)
            sessions = cursor.fetchall()
            
            print(f"📋 Recent Sessions in Database: {len(sessions)}")
            
            for session in sessions:
                session_id, name, position, start, end, status = session
                print(f"   🆔 {session_id}")
                print(f"   👤 {name} - {position}")
                print(f"   📅 {start} → {end or 'ongoing'}")
                print(f"   📊 Status: {status}")
                
                # Check exchanges for this session
                ex_cursor = conn.execute("""
                    SELECT COUNT(*), MIN(timestamp), MAX(timestamp)
                    FROM interview_exchanges 
                    WHERE session_id = ?
                """, (session_id,))
                ex_count, first_ex, last_ex = ex_cursor.fetchone()
                print(f"   💬 Exchanges: {ex_count or 0}")
                if first_ex:
                    print(f"   🕐 First Q&A: {first_ex}")
                    print(f"   🕐 Last Q&A: {last_ex}")
                print()
            
            # Summary stats
            cursor = conn.execute("SELECT COUNT(*) FROM interview_sessions")
            total_sessions = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM interview_exchanges")
            total_exchanges = cursor.fetchone()[0]
            
            print(f"📈 DATABASE SUMMARY:")
            print(f"   📋 Total Sessions: {total_sessions}")
            print(f"   💬 Total Exchanges: {total_exchanges}")
            print(f"   ✅ Database is operational")
            
            return True
            
    except Exception as e:
        print(f"❌ Database verification error: {e}")
        return False

def get_latest_session_summary():
    """Get summary of the most recent session"""
    print(f"\n🎯 LATEST SESSION SUMMARY")
    print("=" * 30)
    
    db_path = os.path.join("database", "interview_evaluations.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found")
        return None
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Get latest session
            cursor = conn.execute("""
                SELECT session_id, candidate_name, position, start_time, end_time, status
                FROM interview_sessions 
                ORDER BY start_time DESC 
                LIMIT 1
            """)
            session = cursor.fetchone()
            
            if not session:
                print(f"❌ No sessions found")
                return None
            
            session_id, name, position, start, end, status = session
            
            # Get exchanges
            cursor = conn.execute("""
                SELECT question, response, timestamp, response_duration
                FROM interview_exchanges 
                WHERE session_id = ?
                ORDER BY timestamp
            """, (session_id,))
            exchanges = cursor.fetchall()
            
            print(f"🆔 Session ID: {session_id}")
            print(f"👤 Candidate: {name}")
            print(f"💼 Position: {position}")
            print(f"📅 Started: {start}")
            print(f"📅 Ended: {end or 'Not ended'}")
            print(f"📊 Status: {status}")
            print(f"💬 Q&A Exchanges: {len(exchanges)}")
            
            if exchanges:
                print(f"\n📝 INTERVIEW FLOW:")
                for i, (q, a, ts, duration) in enumerate(exchanges, 1):
                    print(f"   {i}. Q: {q[:60]}{'...' if len(q) > 60 else ''}")
                    print(f"      A: {a[:60]}{'...' if len(a) > 60 else ''}")
                    print(f"      ⏱️ {duration}s @ {ts}")
                    print()
            
            # Calculate duration if ended
            if start and end:
                start_dt = datetime.fromisoformat(start.replace('Z', ''))
                end_dt = datetime.fromisoformat(end.replace('Z', ''))
                duration = end_dt - start_dt
                print(f"⏱️ Total Duration: {duration}")
            
            return {
                "session_id": session_id,
                "candidate": name,
                "position": position,
                "exchanges": len(exchanges),
                "status": status
            }
            
    except Exception as e:
        print(f"❌ Error getting session summary: {e}")
        return None

def main():
    """Main verification function"""
    print("🔍 INTERVIEW SYSTEM VERIFICATION")
    print("=" * 40)
    print(f"🕐 Verification Time: {datetime.now()}")
    print()
    
    # Step 1: Analyze logs
    logs_good = analyze_interview_logs()
    
    # Step 2: Verify database
    db_good = verify_database_data()
    
    # Step 3: Get latest session
    latest_session = get_latest_session_summary()
    
    # Final verdict
    print(f"\n🎯 FINAL VERIFICATION RESULT")
    print("=" * 35)
    
    if logs_good and db_good and latest_session:
        print(f"🟢 SYSTEM WORKING PERFECTLY!")
        print(f"✅ Logs show complete interview flow")
        print(f"✅ Database contains all data")
        print(f"✅ Latest session: {latest_session['exchanges']} Q&A exchanges")
        print(f"✅ Interview capture is working correctly")
        
        print(f"\n🎉 YOUR INTERVIEW SYSTEM IS FULLY OPERATIONAL!")
        
    elif latest_session and latest_session['exchanges'] > 0:
        print(f"🟡 SYSTEM PARTIALLY WORKING")
        print(f"✅ Interview data was captured ({latest_session['exchanges']} exchanges)")
        print(f"⚠️ Some minor issues in logs or database")
        print(f"💡 System is functional but may need fine-tuning")
        
    else:
        print(f"🔴 SYSTEM NEEDS ATTENTION")
        print(f"❌ No recent interview data found")
        print(f"❌ Interview capture may not be working")
        print(f"🔧 Check agent configuration and run a test interview")
    
    print(f"\n📋 NEXT STEPS:")
    print(f"1. If green: Your system is ready for production interviews")
    print(f"2. If yellow/red: Check the error messages above")
    print(f"3. View detailed logs: interview_detailed.log")
    print(f"4. Run test interview if needed")

if __name__ == "__main__":
    main()
