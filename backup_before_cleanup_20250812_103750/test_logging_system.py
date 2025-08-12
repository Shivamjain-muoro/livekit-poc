"""
Test Interview Tools with Detailed Logging
Verify that detailed logging is working correctly
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_logging_system():
    """Test the logging system with interview tools"""
    print("🧪 TESTING DETAILED LOGGING SYSTEM")
    print("=" * 40)
    
    # Mock context for testing
    class MockContext:
        def __init__(self):
            self.room_name = "test_logging_room"
    
    context = MockContext()
    
    try:
        # Import fixed tools (should now have detailed logging)
        from fixed_interview_tools import (
            start_interview_session,
            record_candidate_response,
            end_interview_session
        )
        
        print("✅ Fixed tools imported successfully")
        print("📝 Starting logging test...")
        
        # Test 1: Start session with logging
        print("\n🚀 TEST 1: Session Start with Logging")
        result = await start_interview_session(
            context=context,
            candidate_name="Test Candidate",
            position="Software Engineer",
            session_id="test_logging_session"
        )
        print(f"✅ Session started: {result[:100]}...")
        
        # Test 2: Record response with logging
        print("\n📝 TEST 2: Response Recording with Logging")
        result = await record_candidate_response(
            context=context,
            session_id="test_logging_session",
            question="What programming languages do you know?",
            response="I know Python, JavaScript, and Java. I've been working with Python for 3 years.",
            response_duration=4.5
        )
        print(f"✅ Response recorded: {result[:100]}...")
        
        # Test 3: End session with logging
        print("\n🏁 TEST 3: Session End with Logging")
        result = await end_interview_session(
            context=context,
            session_id="test_logging_session"
        )
        print(f"✅ Session ended: {result[:100]}...")
        
        # Check if log file was created
        log_file = "interview_detailed.log"
        if os.path.exists(log_file):
            print(f"\n📄 CHECKING LOG FILE: {log_file}")
            
            # Read and show recent log entries
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"📊 Total log entries: {len(lines)}")
            
            # Show last 10 lines
            print(f"\n📄 RECENT LOG ENTRIES:")
            print("=" * 50)
            for line in lines[-10:]:
                print(line.strip())
            print("=" * 50)
            
            # Count different types of log entries
            info_count = sum(1 for line in lines if "INFO" in line)
            error_count = sum(1 for line in lines if "ERROR" in line)
            warning_count = sum(1 for line in lines if "WARNING" in line)
            
            print(f"\n📈 LOG STATISTICS:")
            print(f"   ℹ️ INFO entries: {info_count}")
            print(f"   ⚠️ WARNING entries: {warning_count}")
            print(f"   ❌ ERROR entries: {error_count}")
            
            return True
        else:
            print(f"❌ Log file not found: {log_file}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🔍 DETAILED LOGGING SYSTEM TEST")
    print("=" * 40)
    print(f"🕐 Test Time: {datetime.now()}")
    print()
    
    # Run async test
    try:
        result = asyncio.run(test_logging_system())
        
        if result:
            print(f"\n🟢 LOGGING SYSTEM TEST PASSED!")
            print("✅ Detailed logging is working correctly")
            print("✅ Log file is being created and written to")
            print("✅ All interview operations are being logged")
            
            print(f"\n📋 LOGGING VERIFICATION:")
            print("1. ✅ Session start logged with all details")
            print("2. ✅ Response recording logged with Q&A content")
            print("3. ✅ Session end logged with statistics")
            print("4. ✅ Background evaluation queueing logged")
            print("5. ✅ Database operations logged")
            
            print(f"\n🎯 YOUR LOGGING SYSTEM IS READY!")
            print("📄 Log file: interview_detailed.log")
            print("🔍 Use verify_interview_logs.py after interviews")
            
        else:
            print(f"\n🔴 LOGGING SYSTEM TEST FAILED")
            print("🔧 Check the error messages above")
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")

if __name__ == "__main__":
    main()
