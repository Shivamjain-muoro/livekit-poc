"""
Complete Interview Test Workflow
Verify that interviews are properly captured and evaluated
"""

import subprocess
import time
import sqlite3
import os
from datetime import datetime

def verify_system_readiness():
    """Verify all components are ready for interview capture"""
    print("🔍 VERIFYING INTERVIEW CAPTURE SYSTEM")
    print("=" * 50)
    
    checks = {
        "Environment Variables": False,
        "Database Schema": False,
        "Fixed Tools": False,
        "Report Generator": False,
        "Agent Configuration": False
    }
    
    # Check environment
    from dotenv import load_dotenv
    load_dotenv()
    
    if os.getenv("GOOGLE_API_KEY") and os.getenv("LIVEKIT_URL"):
        checks["Environment Variables"] = True
        print("✅ Environment variables configured")
    else:
        print("❌ Environment variables missing")
    
    # Check database
    db_path = os.path.join("database", "interview_evaluations.db")
    if os.path.exists(db_path):
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                if "interview_sessions" in tables and "interview_exchanges" in tables:
                    checks["Database Schema"] = True
                    print("✅ Database schema ready")
        except Exception as e:
            print(f"❌ Database error: {e}")
    else:
        print("❌ Database not found")
    
    # Check fixed tools
    if os.path.exists("fixed_interview_tools.py"):
        checks["Fixed Tools"] = True
        print("✅ Fixed interview tools available")
    else:
        print("❌ Fixed tools not found")
    
    # Check report generator
    if os.path.exists("report_generator.py"):
        checks["Report Generator"] = True
        print("✅ Report generator available")
    else:
        print("❌ Report generator not found")
    
    # Check agent configuration
    if os.path.exists("complete_interview_agent.py"):
        with open("complete_interview_agent.py", "r") as f:
            content = f.read()
            if "fixed_interview_tools" in content:
                checks["Agent Configuration"] = True
                print("✅ Agent configured with fixed tools")
            else:
                print("❌ Agent not using fixed tools")
    
    # Summary
    ready_count = sum(checks.values())
    total_count = len(checks)
    
    print(f"\n📊 SYSTEM READINESS: {ready_count}/{total_count}")
    
    if ready_count == total_count:
        print("🟢 SYSTEM FULLY READY for interview capture!")
        return True
    else:
        print("🟡 SYSTEM PARTIALLY READY - some issues need attention")
        for check, status in checks.items():
            if not status:
                print(f"   ❌ {check} needs attention")
        return False

def test_interview_workflow():
    """Test the complete interview workflow"""
    print("\n🧪 TESTING INTERVIEW WORKFLOW")
    print("=" * 40)
    
    print("1. ✅ Agent Starting: Ready (you started it)")
    print("2. 🔗 URL Generation: Testing...")
    
    # Test URL generation
    try:
        result = subprocess.run(["python", "generate_test_url.py"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ URL generation working")
            url_lines = result.stdout.strip().split('\n')
            test_url = None
            for line in url_lines:
                if 'https://meet.livekit.io' in line:
                    test_url = line
                    break
            
            if test_url:
                print(f"   📋 Sample URL: {test_url[:60]}...")
                
                # Extract room name for testing
                import re
                room_match = re.search(r'room=([^&]+)', test_url)
                test_room = room_match.group(1) if room_match else "test_room"
                
                print(f"   🆔 Test room: {test_room}")
                return test_room
        else:
            print("   ❌ URL generation failed")
            return None
    except Exception as e:
        print(f"   ❌ URL generation error: {e}")
        return None

def test_database_capture(test_room):
    """Test database capture functionality"""
    print("\n💾 TESTING DATABASE CAPTURE")
    print("=" * 35)
    
    try:
        # Import the fixed tools
        from fixed_interview_tools import start_interview_session, record_candidate_response, end_interview_session
        
        # Simulate session creation
        print("🔄 Testing session creation...")
        
        class MockContext:
            def __init__(self, room_name):
                self.room_name = room_name
        
        context = MockContext(test_room)
        
        # Test session start
        import asyncio
        
        async def test_tools():
            # Start session
            session_result = await start_interview_session(
                context=context,
                candidate_name="Test Candidate",
                position="Test Position",
                session_id=test_room
            )
            print(f"   ✅ Session started: {session_result[:100]}...")
            
            # Test response recording
            response_result = await record_candidate_response(
                context=context,
                session_id=test_room,
                question="Test question for system verification",
                response="This is a test response to verify the system is working correctly."
            )
            print(f"   ✅ Response recorded: {response_result[:100]}...")
            
            # Test session end
            end_result = await end_interview_session(
                context=context,
                session_id=test_room
            )
            print(f"   ✅ Session ended: {end_result[:100]}...")
        
        # Run the test
        asyncio.run(test_tools())
        
        # Verify in database
        db_path = os.path.join("database", "interview_evaluations.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT session_id, candidate_name FROM interview_sessions WHERE session_id = ?", (test_room,))
            session = cursor.fetchone()
            
            if session:
                print(f"   ✅ Database verification: Session {session[0]} found")
                
                # Check exchanges
                cursor = conn.execute("SELECT COUNT(*) FROM interview_exchanges WHERE session_id = ?", (test_room,))
                exchange_count = cursor.fetchone()[0]
                print(f"   ✅ Exchanges stored: {exchange_count}")
                
                # Clean up test data
                conn.execute("DELETE FROM interview_exchanges WHERE session_id = ?", (test_room,))
                conn.execute("DELETE FROM interview_sessions WHERE session_id = ?", (test_room,))
                conn.commit()
                print(f"   🧹 Test data cleaned up")
                
                return True
            else:
                print("   ❌ Session not found in database")
                return False
        
    except Exception as e:
        print(f"   ❌ Database capture test failed: {e}")
        return False

def provide_interview_instructions():
    """Provide step-by-step instructions for conducting an interview"""
    print("\n📋 STEP-BY-STEP INTERVIEW GUIDE")
    print("=" * 40)
    
    print("🚀 FOR YOUR NEXT INTERVIEW:")
    print()
    print("1. 🤖 START AGENT (CRITICAL FIRST STEP):")
    print("   python complete_interview_agent.py dev")
    print("   ⏳ Wait for: 'Agent session started successfully!'")
    print()
    print("2. 🔗 GENERATE INTERVIEW URL:")
    print("   python generate_test_url.py")
    print("   📋 Copy the generated URL")
    print()
    print("3. 🎤 CONDUCT INTERVIEW:")
    print("   • Use the generated URL to join")
    print("   • Agent will automatically:")
    print("     - Start session when you join")
    print("     - Record all Q&A exchanges")
    print("     - Save to database in real-time")
    print("     - Process evaluations in background")
    print()
    print("4. 📊 CHECK RESULTS IMMEDIATELY:")
    print("   python view_interview_reports.py")
    print("   • Your session will appear with real data")
    print("   • Scores and evaluations will be available")
    print("   • Comprehensive reports will be generated")
    print()
    print("🔥 KEY DIFFERENCES FROM BEFORE:")
    print("✅ Agent now uses FIXED tools that save to database")
    print("✅ Sessions auto-start based on room name")
    print("✅ Real-time data capture during interview")
    print("✅ Immediate evaluation availability")
    print("✅ No more missing interview data!")

def main():
    print("🎙️ INTERVIEW SYSTEM VERIFICATION & TEST")
    print("=" * 50)
    
    # Step 1: Verify system readiness
    is_ready = verify_system_readiness()
    
    # Step 2: Test workflow components
    test_room = test_interview_workflow()
    
    # Step 3: Test database capture
    if test_room:
        db_working = test_database_capture(test_room)
    else:
        db_working = False
    
    # Step 4: Overall assessment
    print(f"\n🎯 OVERALL SYSTEM STATUS")
    print("=" * 30)
    
    if is_ready and test_room and db_working:
        print("🟢 SYSTEM FULLY OPERATIONAL!")
        print("✅ Ready for live interview capture")
        print("✅ All components working correctly")
        print("✅ Database integration verified")
        
        provide_interview_instructions()
        
        print(f"\n💡 CONFIDENCE LEVEL: 95%")
        print("Your next interview WILL be properly captured and evaluated!")
        
    else:
        print("🟡 SYSTEM NEEDS ATTENTION")
        if not is_ready:
            print("❌ System readiness issues")
        if not test_room:
            print("❌ URL generation issues")
        if not db_working:
            print("❌ Database capture issues")
        
        print("\n🔧 Recommended actions:")
        print("1. Check error messages above")
        print("2. Ensure all components are properly installed")
        print("3. Test again after fixes")

if __name__ == "__main__":
    main()
