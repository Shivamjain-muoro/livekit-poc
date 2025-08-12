"""
Simple Interview Checker and Agent Starter
Check for recent interviews and start agent properly
"""

import os
import subprocess
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment
load_dotenv()

def check_for_recent_interviews():
    """Check for any recent interview activity"""
    print("🔍 CHECKING FOR RECENT INTERVIEW ACTIVITY")
    print("=" * 50)
    
    db_path = os.path.join("database", "interview_evaluations.db")
    
    if not os.path.exists(db_path):
        print("❌ No database found")
        return []
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Get all sessions from today
            today = datetime.now().strftime("%Y-%m-%d")
            cursor = conn.execute("""
                SELECT session_id, candidate_name, start_time, overall_score, status
                FROM interview_sessions 
                WHERE start_time LIKE ?
                ORDER BY start_time DESC
            """, (f"{today}%",))
            
            sessions = cursor.fetchall()
            
            print(f"📅 Sessions from today ({today}): {len(sessions)}")
            
            recent_sessions = []
            for session in sessions:
                session_id, name, start_time, score, status = session
                print(f"\n📋 Session: {session_id}")
                print(f"   👤 Candidate: {name}")
                print(f"   🕐 Time: {start_time}")
                print(f"   📊 Score: {score or 0}")
                print(f"   📋 Status: {status}")
                
                # Check exchanges
                ex_cursor = conn.execute("""
                    SELECT COUNT(*), MAX(timestamp) 
                    FROM interview_exchanges 
                    WHERE session_id = ?
                """, (session_id,))
                ex_count, last_exchange = ex_cursor.fetchone()
                print(f"   💬 Exchanges: {ex_count or 0}")
                
                if last_exchange:
                    print(f"   🕐 Last activity: {last_exchange}")
                
                # Determine if this is a real session
                if name != "John Test" or ex_count > 1:
                    print("   ✅ This looks like a REAL interview session!")
                    recent_sessions.append(session)
                else:
                    print("   🤖 This is a test session")
            
            return recent_sessions
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return []

def start_agent_properly():
    """Start the agent in development mode"""
    print("\n🚀 STARTING LIVEKIT AGENT PROPERLY")
    print("=" * 40)
    
    # Check environment
    google_key = os.getenv("GOOGLE_API_KEY")
    livekit_url = os.getenv("LIVEKIT_URL")
    
    if not google_key:
        print("❌ GOOGLE_API_KEY not found")
        return False
    
    if not livekit_url:
        print("❌ LIVEKIT_URL not found")
        return False
    
    print(f"✅ GOOGLE_API_KEY: {google_key[:8]}...")
    print(f"✅ LIVEKIT_URL: {livekit_url}")
    
    # Start agent in development mode
    print("\n🔄 Starting agent in development mode...")
    print("📺 This will open a new window with the agent")
    
    try:
        # Use start command to open new window
        cmd = ["start", "cmd", "/k", "python", "complete_interview_agent.py", "dev"]
        subprocess.Popen(cmd, shell=True)
        print("✅ Agent started in new window!")
        print("🔍 Check the new terminal for 'Agent session started successfully!'")
        return True
        
    except Exception as e:
        print(f"❌ Error starting agent: {e}")
        return False

def generate_interview_url():
    """Generate a fresh interview URL"""
    print("\n🔗 GENERATING FRESH INTERVIEW URL")
    print("=" * 35)
    
    try:
        result = subprocess.run(["python", "generate_test_url.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ New interview URL generated!")
            print("\n📋 COPY THIS URL:")
            print("-" * 50)
            print(result.stdout)
            print("-" * 50)
            return True
        else:
            print("❌ Error generating URL:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ URL generation timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🎙️ INTERVIEW STATUS CHECKER & AGENT STARTER")
    print("=" * 55)
    
    # Step 1: Check for recent interviews
    recent_sessions = check_for_recent_interviews()
    
    if recent_sessions:
        print(f"\n✅ FOUND {len(recent_sessions)} RECENT REAL INTERVIEWS!")
        print("🎯 Let's check the evaluations for these sessions...")
        
        # Show recent interview details
        for session in recent_sessions[:3]:  # Show up to 3 recent
            session_id = session[0]
            print(f"\n📊 Getting evaluation for: {session_id}")
            
            try:
                # Try to get comprehensive report
                result = subprocess.run([
                    "python", "-c", 
                    f"from report_generator import generate_session_report; "
                    f"import os; import json; "
                    f"report = generate_session_report('{session_id}', os.getenv('GOOGLE_API_KEY')); "
                    f"print(json.dumps(report, indent=2) if 'error' not in report else f'Report not ready: {{report[\"error\"]}}')"
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0 and "error" not in result.stdout.lower():
                    print("✅ Evaluation available!")
                    # Show summary
                    lines = result.stdout.split('\n')[:10]  # First 10 lines
                    for line in lines:
                        print(f"   {line}")
                else:
                    print("⚠️ Evaluation still processing or error occurred")
                    
            except Exception as e:
                print(f"⚠️ Could not get evaluation: {e}")
    
    else:
        print("\n❌ NO RECENT REAL INTERVIEWS FOUND")
        print("💡 Your recent interview was not captured by the agent")
        print("🔧 Let's set up proper capture for next interview...")
    
    # Step 2: Offer to start agent for future interviews
    print(f"\n🎯 NEXT STEPS:")
    print("1. Start agent for future interviews")
    print("2. Generate new interview URL")
    print("3. View existing reports")
    print("4. Exit")
    
    choice = input("\nChoose option (1-4): ").strip()
    
    if choice == "1":
        start_agent_properly()
        print("\n💡 IMPORTANT: Wait for 'Agent session started successfully!' message")
        print("💡 Then generate a URL and conduct interview")
        
    elif choice == "2":
        generate_interview_url()
        print("\n💡 Use this URL for your interview")
        print("⚠️ Make sure the agent is running first!")
        
    elif choice == "3":
        print("\n📊 Opening interview reports...")
        subprocess.run(["python", "view_interview_reports.py"])
        
    elif choice == "4":
        print("👋 Goodbye!")
    
    print(f"\n🎯 SUMMARY:")
    print("✅ For future interviews: Start agent first, then use generated URL")
    print("✅ Agent must be running to capture interview data")
    print("✅ Check reports after interview completion")

if __name__ == "__main__":
    main()
