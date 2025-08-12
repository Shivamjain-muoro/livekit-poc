"""
Complete Interview Workflow - Step by Step Guide
Ensure your interviews are properly captured with real data
"""

import subprocess
import time
import os
import sys

def check_prerequisites():
    """Check if all files and environment are ready"""
    print("🔍 CHECKING PREREQUISITES...")
    
    required_files = [
        "complete_interview_agent.py",
        "generate_test_url.py", 
        "fast_interview_tools.py",
        "background_evaluator.py",
        "report_generator.py"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file}")
            missing_files.append(file)
    
    # Check environment
    if os.getenv("GOOGLE_API_KEY"):
        print("   ✅ GOOGLE_API_KEY configured")
    else:
        print("   ❌ GOOGLE_API_KEY missing")
        missing_files.append("GOOGLE_API_KEY")
    
    if os.getenv("LIVEKIT_URL"):
        print("   ✅ LIVEKIT_URL configured")
    else:
        print("   ❌ LIVEKIT_URL missing")
        missing_files.append("LIVEKIT_URL")
    
    return len(missing_files) == 0, missing_files

def start_agent_properly():
    """Start the agent with proper monitoring"""
    print("\n🚀 STARTING INTERVIEW AGENT...")
    print("This is the CRITICAL step - the agent must be running!")
    
    # Start agent
    print("Starting agent in new terminal window...")
    
    # For Windows, start in new command window
    try:
        cmd = ["start", "cmd", "/k", "python", "complete_interview_agent.py"]
        subprocess.Popen(cmd, shell=True)
        print("✅ Agent started in new window")
        print("📺 Check the new terminal window for agent status")
        return True
    except Exception as e:
        print(f"❌ Error starting agent: {e}")
        return False

def generate_interview_url():
    """Generate a new interview URL"""
    print("\n🔗 GENERATING INTERVIEW URL...")
    
    try:
        result = subprocess.run(["python", "generate_test_url.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ URL generated successfully!")
            print("📋 Output:")
            print(result.stdout)
            return True
        else:
            print("❌ Error generating URL:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def wait_for_interview():
    """Wait for interview to complete"""
    print("\n⏳ WAITING FOR INTERVIEW...")
    print("1. Use the generated URL to join the interview")
    print("2. Conduct the interview naturally")
    print("3. The agent will automatically capture everything")
    print("4. Press Enter here when the interview is complete")
    
    input("Press Enter when interview is done...")

def check_results():
    """Check if the interview was captured"""
    print("\n📊 CHECKING INTERVIEW RESULTS...")
    
    try:
        result = subprocess.run(["python", "view_interview_reports.py"], 
                              input="1\n5\n", text=True, capture_output=True)
        
        if "AVAILABLE INTERVIEW SESSIONS" in result.stdout:
            print("✅ Database accessible")
            
            # Check for recent sessions
            if "Real Candidate" in result.stdout or "interview_" in result.stdout:
                print("✅ New interview session found!")
                return True
            else:
                print("❌ No new interview sessions found")
                print("The interview may not have been captured properly")
                return False
        else:
            print("❌ Error accessing interview database")
            return False
            
    except Exception as e:
        print(f"❌ Error checking results: {e}")
        return False

def main():
    print("🎙️ COMPLETE INTERVIEW WORKFLOW")
    print("=" * 50)
    print("This guide ensures your interviews are properly captured!")
    
    # Step 1: Check prerequisites
    ready, missing = check_prerequisites()
    if not ready:
        print(f"\n❌ Missing requirements: {missing}")
        print("Please ensure all files exist and environment is configured")
        return
    
    print("\n✅ All prerequisites ready!")
    
    # Interactive workflow
    while True:
        print("\n🎯 INTERVIEW WORKFLOW STEPS:")
        print("1. Start Interview Agent (CRITICAL)")
        print("2. Generate Interview URL")
        print("3. Conduct Interview") 
        print("4. Check Results")
        print("5. View All Reports")
        print("6. Exit")
        
        choice = input("\nChoose step (1-6): ").strip()
        
        if choice == "1":
            success = start_agent_properly()
            if success:
                print("\n✅ Agent started!")
                print("🔄 Wait 10-15 seconds for agent to fully initialize")
                print("📺 Check the new terminal window for 'Agent session started successfully!'")
        
        elif choice == "2":
            success = generate_interview_url()
            if success:
                print("\n✅ URL generated!")
                print("📋 Copy the URL and use it for your interview")
        
        elif choice == "3":
            wait_for_interview()
            print("✅ Interview completed!")
        
        elif choice == "4":
            success = check_results()
            if success:
                print("✅ Interview was captured successfully!")
            else:
                print("❌ Interview was not captured")
                print("💡 Make sure the agent was running during the interview")
        
        elif choice == "5":
            print("\n📊 Opening interview reports...")
            subprocess.run(["python", "view_interview_reports.py"])
        
        elif choice == "6":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
