"""
Real-Time Interview Capture System
Ensure interviews are properly captured with live monitoring
"""

import subprocess
import time
import os
import sqlite3
from datetime import datetime
import threading
import signal
import sys

class LiveInterviewMonitor:
    """Monitor interviews in real-time and ensure capture"""
    
    def __init__(self):
        self.db_path = os.path.join("database", "interview_evaluations.db")
        self.monitoring = False
        self.agent_process = None
        self.last_session_count = 0
        
    def start_agent_with_monitoring(self):
        """Start the agent with proper monitoring"""
        print("🚀 STARTING INTERVIEW AGENT WITH MONITORING")
        print("=" * 50)
        
        # Check environment first
        if not os.getenv("GOOGLE_API_KEY"):
            print("❌ GOOGLE_API_KEY not set!")
            return False
            
        if not os.getenv("LIVEKIT_URL"):
            print("❌ LIVEKIT_URL not set!")
            return False
        
        print("✅ Environment variables configured")
        
        # Start the agent process
        try:
            print("🔄 Starting LiveKit agent...")
            cmd = ["python", "complete_interview_agent.py", "dev"]
            
            self.agent_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            print(f"✅ Agent started with PID: {self.agent_process.pid}")
            
            # Start monitoring thread
            self.monitoring = True
            monitor_thread = threading.Thread(target=self.monitor_agent_output)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Start database monitoring thread
            db_thread = threading.Thread(target=self.monitor_database)
            db_thread.daemon = True
            db_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Error starting agent: {e}")
            return False
    
    def monitor_agent_output(self):
        """Monitor agent output in real-time"""
        print("🔍 MONITORING AGENT OUTPUT...")
        
        while self.monitoring and self.agent_process:
            try:
                # Read stdout
                if self.agent_process.stdout:
                    line = self.agent_process.stdout.readline()
                    if line:
                        print(f"🤖 AGENT: {line.strip()}")
                        
                        # Check for key messages
                        if "Agent session started successfully" in line:
                            print("✅ AGENT READY FOR INTERVIEWS!")
                        elif "participant joined" in line.lower():
                            print("👤 PARTICIPANT JOINED - INTERVIEW STARTING!")
                        elif "session_id" in line.lower():
                            print("💾 SESSION DATA DETECTED!")
                
                # Check if process is still running
                if self.agent_process.poll() is not None:
                    print("⚠️ Agent process has stopped")
                    break
                    
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error monitoring agent: {e}")
                break
    
    def monitor_database(self):
        """Monitor database for new sessions"""
        print("📊 MONITORING DATABASE FOR NEW SESSIONS...")
        
        # Get initial count
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM interview_sessions")
                self.last_session_count = cursor.fetchone()[0]
                print(f"📋 Initial session count: {self.last_session_count}")
        except:
            self.last_session_count = 0
        
        while self.monitoring:
            try:
                time.sleep(5)  # Check every 5 seconds
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM interview_sessions")
                    current_count = cursor.fetchone()[0]
                    
                    if current_count > self.last_session_count:
                        print(f"🆕 NEW SESSION DETECTED! Count: {self.last_session_count} → {current_count}")
                        
                        # Get the new session details
                        cursor = conn.execute("""
                            SELECT session_id, candidate_name, start_time
                            FROM interview_sessions 
                            ORDER BY start_time DESC LIMIT 1
                        """)
                        session = cursor.fetchone()
                        if session:
                            session_id, name, start_time = session
                            print(f"🎤 NEW INTERVIEW: {session_id} | {name} | {start_time}")
                        
                        self.last_session_count = current_count
                    
                    # Also check for new exchanges
                    cursor = conn.execute("""
                        SELECT session_id, COUNT(*) as exchange_count
                        FROM interview_exchanges 
                        GROUP BY session_id
                        ORDER BY MAX(timestamp) DESC LIMIT 3
                    """)
                    exchanges = cursor.fetchall()
                    
                    for session_id, count in exchanges:
                        if count > 0:
                            print(f"💬 {session_id}: {count} exchanges")
                
            except Exception as e:
                print(f"❌ Database monitoring error: {e}")
                time.sleep(5)
    
    def stop_monitoring(self):
        """Stop monitoring and clean up"""
        print("🔚 STOPPING MONITORING...")
        self.monitoring = False
        
        if self.agent_process:
            print("🔚 Terminating agent process...")
            self.agent_process.terminate()
            try:
                self.agent_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("🔨 Force killing agent process...")
                self.agent_process.kill()
    
    def check_current_status(self):
        """Check current system status"""
        print("\n📊 CURRENT SYSTEM STATUS:")
        print("-" * 30)
        
        # Check database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM interview_sessions")
                session_count = cursor.fetchone()[0]
                print(f"📋 Total sessions in database: {session_count}")
                
                # Get latest session
                cursor = conn.execute("""
                    SELECT session_id, candidate_name, start_time, overall_score
                    FROM interview_sessions 
                    ORDER BY start_time DESC LIMIT 1
                """)
                latest = cursor.fetchone()
                if latest:
                    session_id, name, start_time, score = latest
                    print(f"🕐 Latest session: {session_id}")
                    print(f"👤 Candidate: {name}")
                    print(f"📅 Time: {start_time}")
                    print(f"📊 Score: {score or 0}")
        except Exception as e:
            print(f"❌ Database error: {e}")
        
        # Check agent process
        if self.agent_process and self.agent_process.poll() is None:
            print(f"✅ Agent running (PID: {self.agent_process.pid})")
        else:
            print("❌ Agent not running")

def main():
    monitor = LiveInterviewMonitor()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n🔚 Shutting down...")
        monitor.stop_monitoring()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🎙️ LIVE INTERVIEW MONITORING SYSTEM")
    print("=" * 50)
    
    while True:
        print("\n🎯 OPTIONS:")
        print("1. Start Agent with Live Monitoring")
        print("2. Check Current Status")
        print("3. Generate New Interview URL")
        print("4. View Latest Reports")
        print("5. Stop and Exit")
        
        choice = input("\nChoose option (1-5): ").strip()
        
        if choice == "1":
            if monitor.start_agent_with_monitoring():
                print("\n✅ AGENT STARTED WITH MONITORING!")
                print("🔄 Agent is now ready to capture interviews")
                print("📊 Database monitoring active")
                print("💡 Generate a URL and conduct your interview")
                print("⌨️ Press Ctrl+C to stop the agent")
                
                try:
                    # Keep monitoring running
                    while monitor.monitoring and monitor.agent_process and monitor.agent_process.poll() is None:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🔚 Stopping agent...")
                    monitor.stop_monitoring()
        
        elif choice == "2":
            monitor.check_current_status()
        
        elif choice == "3":
            print("\n🔗 GENERATING INTERVIEW URL...")
            try:
                result = subprocess.run(["python", "generate_test_url.py"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ URL generated:")
                    print(result.stdout)
                else:
                    print("❌ Error generating URL:")
                    print(result.stderr)
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == "4":
            print("\n📊 OPENING REPORTS...")
            subprocess.run(["python", "view_interview_reports.py"])
        
        elif choice == "5":
            monitor.stop_monitoring()
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
