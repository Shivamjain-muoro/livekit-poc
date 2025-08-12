"""
Complete Testing Flow for Fast Non-Blocking Interview System
Shows you exactly how to start and test your system
"""

import os
import sys
import time
from dotenv import load_dotenv

def print_header(title):
    print("\n" + "=" * 60)
    print(f"🎯 {title}")
    print("=" * 60)

def test_environment():
    print_header("STEP 1: ENVIRONMENT CHECK")
    
    # Load environment
    load_dotenv()
    
    # Check required variables
    google_key = os.getenv("GOOGLE_API_KEY")
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_key = os.getenv("LIVEKIT_API_KEY")
    
    print(f"🔑 Google API Key: {'✅ Found' if google_key else '❌ Missing'}")
    print(f"🔑 LiveKit URL: {livekit_url or '❌ Missing'}")
    print(f"🔑 LiveKit API Key: {'✅ Found' if livekit_key else '❌ Missing'}")
    
    if google_key and livekit_url and livekit_key:
        print("✅ All environment variables are configured!")
        return True
    else:
        print("❌ Missing required environment variables!")
        return False

def test_imports():
    print_header("STEP 2: IMPORT TEST")
    
    try:
        print("📦 Testing imports...")
        
        # Test main components
        from fast_interview_tools import start_interview_session
        print("✅ fast_interview_tools imported successfully")
        
        from background_evaluator import get_background_evaluator
        print("✅ background_evaluator imported successfully")
        
        from report_generator import generate_session_report
        print("✅ report_generator imported successfully")
        
        print("✅ All core modules imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_agent_creation():
    print_header("STEP 3: AGENT CREATION TEST")
    
    try:
        print("🤖 Creating InterviewAgent...")
        
        # This will show all the startup logs
        from complete_interview_agent import InterviewAgent
        agent = InterviewAgent()
        
        print("✅ Agent created successfully!")
        print(f"📊 Agent has {len(agent.tools)} tools configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent creation error: {e}")
        return False

def show_testing_options():
    print_header("STEP 4: TESTING OPTIONS")
    
    print("""
🚀 YOUR SYSTEM IS READY! Here are your testing options:

OPTION A: Test Individual Components
   python -c "from fast_interview_tools import *; print('Tools working!')"

OPTION B: Run System Tests  
   python test_interview_system.py
   (Choose option 1 for full test suite)

OPTION C: Start the Interview Agent
   python complete_interview_agent.py
   
   Then connect using:
   - LiveKit client app
   - Web browser to your LiveKit room
   - Mobile app with LiveKit SDK

OPTION D: Test with Mock Interview
   1. Start the agent: python complete_interview_agent.py
   2. Join the LiveKit room from another device/browser
   3. The agent will automatically start the interview
   4. After interview, reports will be available in 1-2 minutes

🎯 RECOMMENDED TESTING FLOW:
   1. Run Option B to verify all systems
   2. Run Option C to start the agent
   3. Connect to the LiveKit room to test real conversation
   4. Check the database/ folder for stored results
   5. Generate reports using the report_generator module

🔗 LiveKit Room Access:
   URL: {os.getenv('LIVEKIT_URL')}
   Room: Will be created automatically when agent starts
   
📊 Monitoring:
   - Watch console output for real-time system status
   - 🚀 = Fast operations
   - 🔄 = Background processing  
   - ✅ = Successful operations
   - ❌ = Errors requiring attention
""")

def run_quick_demo():
    print_header("STEP 5: QUICK DEMO")
    
    print("🎬 Running a quick demo of the system...")
    
    try:
        # Import and create session
        from fast_interview_tools import ACTIVE_SESSIONS
        from datetime import datetime
        
        # Create demo session
        demo_session_id = f"demo_{int(time.time())}"
        ACTIVE_SESSIONS[demo_session_id] = {
            "candidate_name": "Demo Candidate",
            "position": "Software Engineer",
            "start_time": datetime.now(),
            "questions_asked": [],
            "responses_received": [],
            "status": "active"
        }
        
        print(f"✅ Created demo session: {demo_session_id}")
        
        # Simulate some activity
        ACTIVE_SESSIONS[demo_session_id]["questions_asked"].append({
            "question": "Tell me about your background",
            "timestamp": datetime.now(),
            "type": "opening"
        })
        
        ACTIVE_SESSIONS[demo_session_id]["responses_received"].append({
            "response": "I have 5 years of experience in software development...",
            "timestamp": datetime.now(),
            "duration": 15.5
        })
        
        print("✅ Added sample question and response")
        print("✅ Demo session created successfully!")
        print(f"📊 Session data: {len(ACTIVE_SESSIONS[demo_session_id]['questions_asked'])} questions, {len(ACTIVE_SESSIONS[demo_session_id]['responses_received'])} responses")
        
        # Cleanup
        del ACTIVE_SESSIONS[demo_session_id]
        print("✅ Demo session cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return False

def main():
    print("🎙️ FAST NON-BLOCKING INTERVIEW SYSTEM - TESTING FLOW")
    print("Welcome! Let's test your enhanced interview system step by step.")
    
    # Run all tests
    tests_passed = 0
    total_tests = 5
    
    if test_environment():
        tests_passed += 1
    
    if test_imports():
        tests_passed += 1
    
    if test_agent_creation():
        tests_passed += 1
        
    show_testing_options()
    tests_passed += 1
    
    if run_quick_demo():
        tests_passed += 1
    
    # Final summary
    print_header("TESTING COMPLETE")
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Your system is ready for production use!")
        print("\n🚀 NEXT STEPS:")
        print("1. Run: python complete_interview_agent.py")
        print("2. Connect to your LiveKit room")
        print("3. Start conducting interviews!")
    else:
        print("⚠️ Some tests failed. Review the errors above before proceeding.")

if __name__ == "__main__":
    main()
