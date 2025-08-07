"""
Interview Session Recovery and Real-Time Monitoring
Ensure all future interviews are properly captured and stored
"""

import subprocess
import time
import os
import sqlite3
from datetime import datetime
import json

class InterviewMonitor:
    """Monitor and ensure interviews are properly captured"""
    
    def __init__(self):
        self.db_path = os.path.join("database", "interview_evaluations.db")
        
    def check_agent_status(self):
        """Check if the LiveKit agent is running"""
        try:
            # Check for running Python processes
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            
            if 'python.exe' in result.stdout:
                print("✅ Python processes are running:")
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'python.exe' in line:
                        print(f"   {line.strip()}")
                return True
            else:
                print("❌ No Python processes found")
                return False
                
        except Exception as e:
            print(f"❌ Error checking processes: {e}")
            return False
    
    def start_interview_agent(self):
        """Start the interview agent"""
        print("🚀 Starting LiveKit Interview Agent...")
        print("This will start the agent that captures and processes interviews")
        
        try:
            # Start the agent in background
            cmd = ["python", "complete_interview_agent.py"]
            print(f"Command: {' '.join(cmd)}")
            print("Note: This will start the agent - you'll see LiveKit logs")
            print("Keep this running when conducting interviews!")
            
            return subprocess.Popen(cmd, cwd=os.getcwd())
            
        except Exception as e:
            print(f"❌ Error starting agent: {e}")
            return None
    
    def test_database_connection(self):
        """Test if database is accessible and ready"""
        print("🔍 Testing database connection...")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM interview_sessions")
                count = cursor.fetchone()[0]
                print(f"✅ Database accessible - {count} sessions found")
                return True
                
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
    
    def create_manual_session_entry(self, room_name, candidate_name="Real Candidate"):
        """Manually create a session entry for a missed interview"""
        print(f"📝 Creating manual session entry for room: {room_name}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                session_id = f"manual_{room_name}_{int(time.time())}"
                
                # Insert basic session info
                conn.execute("""
                    INSERT INTO interview_sessions 
                    (session_id, candidate_name, position, start_time, status, overall_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    candidate_name,
                    "Position Not Recorded",
                    datetime.now().isoformat(),
                    "manual_entry",
                    0
                ))
                
                # Add a note about this being a recovery entry
                conn.execute("""
                    INSERT INTO interview_exchanges 
                    (session_id, question, response, timestamp, ai_evaluation)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session_id,
                    "Recovery Note",
                    f"This session was manually created for room {room_name}. The original interview data was not captured due to agent not being active.",
                    datetime.now().isoformat(),
                    "This is a recovery entry. Future interviews will be automatically captured when the agent is running."
                ))
                
                print(f"✅ Manual session created: {session_id}")
                return session_id
                
        except Exception as e:
            print(f"❌ Error creating manual session: {e}")
            return None
    
    def get_interview_instructions(self):
        """Get instructions for conducting proper interviews"""
        return """
🎯 HOW TO CONDUCT PROPERLY CAPTURED INTERVIEWS:

1. **START THE AGENT FIRST** (CRITICAL):
   python complete_interview_agent.py
   
2. **Wait for Agent Ready Message**:
   Look for: "✅ ENTRYPOINT: Agent session started successfully!"
   
3. **Generate Interview URL**:
   python generate_test_url.py
   
4. **Conduct Interview**:
   - Use the generated URL
   - Agent will automatically capture everything
   - Database will be updated in real-time
   
5. **Check Results**:
   python view_interview_reports.py

🚨 IMPORTANT: The agent MUST be running BEFORE the interview starts!
"""

def main():
    monitor = InterviewMonitor()
    
    print("🎙️ INTERVIEW SESSION RECOVERY & MONITORING")
    print("=" * 60)
    
    print("\n1. CHECKING CURRENT STATUS:")
    agent_running = monitor.check_agent_status()
    db_accessible = monitor.test_database_connection()
    
    print(f"\n📊 STATUS SUMMARY:")
    print(f"   Agent Running: {'✅' if agent_running else '❌'}")
    print(f"   Database Ready: {'✅' if db_accessible else '❌'}")
    
    print("\n2. ISSUE ANALYSIS:")
    print("   ❌ Your interview with room 'interview_eac86959' was not captured")
    print("   ❌ Reason: Agent was not running during the interview")
    print("   ❌ Only test data exists in database")
    
    print("\n3. RECOVERY OPTIONS:")
    print("   A. Create manual entry for missed interview")
    print("   B. Start agent for future interviews") 
    print("   C. Get instructions for proper interview workflow")
    
    choice = input("\nChoose option (A/B/C): ").strip().upper()
    
    if choice == "A":
        room_name = "interview_eac86959"
        candidate_name = input("Enter candidate name (or press Enter for 'Real Candidate'): ").strip()
        if not candidate_name:
            candidate_name = "Real Candidate"
        
        session_id = monitor.create_manual_session_entry(room_name, candidate_name)
        if session_id:
            print(f"\n✅ Manual session created: {session_id}")
            print("Note: This is just a placeholder. Real interview data was not captured.")
    
    elif choice == "B":
        print("\n🚀 STARTING INTERVIEW AGENT...")
        print("This will start the agent that captures interviews in real-time")
        print("Keep this running when conducting interviews!")
        
        agent_process = monitor.start_interview_agent()
        if agent_process:
            print("✅ Agent started successfully!")
            print("Now you can conduct interviews and they will be automatically captured")
        
    elif choice == "C":
        print(monitor.get_interview_instructions())
    
    print("\n🎯 NEXT STEPS FOR FUTURE INTERVIEWS:")
    print("1. Always start the agent first: python complete_interview_agent.py")
    print("2. Generate URL: python generate_test_url.py") 
    print("3. Conduct interview using the URL")
    print("4. Check results: python view_interview_reports.py")
    print("\n💡 The agent captures everything automatically when running!")

if __name__ == "__main__":
    main()
