"""
Test Fixed Interview Tools
Verify that the tools work without errors
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

def test_import():
    """Test importing the fixed tools"""
    print("🔍 TESTING IMPORT OF FIXED TOOLS")
    print("=" * 40)
    
    try:
        from fixed_interview_tools import (
            start_interview_session,
            record_candidate_response,
            end_interview_session
        )
        print("✅ Import successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_start_session():
    """Test starting a session"""
    print("\n🚀 TESTING START SESSION")
    print("=" * 30)
    
    try:
        # Import the function
        from fixed_interview_tools import start_interview_session
        
        # Test call (this should work without errors now)
        result = start_interview_session(
            candidate_name="Test Candidate",
            position="Software Engineer"
        )
        
        print("✅ Start session test successful")
        print(f"📊 Result type: {type(result)}")
        return True
        
    except Exception as e:
        print(f"❌ Start session test failed: {e}")
        return False

def test_record_response():
    """Test recording a response"""
    print("\n📝 TESTING RECORD RESPONSE")
    print("=" * 30)
    
    try:
        # First start a session
        from fixed_interview_tools import start_interview_session, record_candidate_response
        
        session_result = start_interview_session(
            candidate_name="Test Candidate",
            position="Software Engineer"
        )
        
        # Parse session_id from result
        import json
        if isinstance(session_result, str):
            session_data = json.loads(session_result)
        else:
            session_data = session_result
            
        session_id = session_data.get("session_id")
        
        if not session_id:
            print("❌ Could not get session_id")
            return False
        
        # Test recording response
        response_result = record_candidate_response(
            session_id=session_id,
            question="What programming languages do you know?",
            response="I know Python, JavaScript, and Java.",
            response_duration=5.2
        )
        
        print("✅ Record response test successful")
        return True
        
    except Exception as e:
        print(f"❌ Record response test failed: {e}")
        return False

def main():
    print("🧪 TESTING FIXED INTERVIEW TOOLS")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_import),
        ("Start Session Test", test_start_session),
        ("Record Response Test", test_record_response)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n📊 TEST RESULTS: {passed}/{total} PASSED")
    
    if passed == total:
        print("🟢 ALL TESTS PASSED!")
        print("✅ The fix is working correctly")
        print("✅ You can now start interviews without errors")
        return True
    else:
        print("🟡 SOME TESTS FAILED")
        print("🔧 Additional fixes may be needed")
        return False

if __name__ == "__main__":
    main()
