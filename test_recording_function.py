"""
Test Recording Function
Tests the record_candidate_response function to make sure it's working
"""

import asyncio
import os
from realtime_interview_tools import record_candidate_response, start_interview_session, get_real_time_progress
from datetime import datetime

async def test_recording_function():
    """Test the recording function to make sure it works"""
    print("🧪 TESTING RECORDING FUNCTION")
    print("=" * 50)
    
    # Create a test session
    test_session_id = f"recording_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"📝 Creating test session: {test_session_id}")
    
    # Start session
    session_result = await start_interview_session(
        context=None,
        candidate_name="Test Candidate",
        position="Test Position", 
        session_id=test_session_id
    )
    print(f"✅ Session created: {session_result}")
    
    # Test getting progress
    progress_result = await get_real_time_progress(context=None, session_id=test_session_id)
    print(f"✅ Progress check: {progress_result}")
    
    # Test recording a conversation exchange
    print(f"\n🎤 Testing conversation recording...")
    
    test_question = "Can you tell me about your background in software development?"
    test_response = "I have 5 years of experience in software development, primarily working with Python and JavaScript. I've built web applications using Django and React, and I'm experienced with databases like PostgreSQL and MongoDB."
    test_duration = 25.0
    
    record_result = await record_candidate_response(
        context=None,
        session_id=test_session_id,
        question=test_question,
        response=test_response,
        response_duration=test_duration
    )
    
    print(f"✅ Recording result: {record_result}")
    
    # Wait a moment for processing
    print(f"\n⏳ Waiting for automated evaluation...")
    await asyncio.sleep(5)
    
    # Check if it was recorded in database
    import sqlite3
    db_path = os.path.join("database", "interview_evaluations.db")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("""
                SELECT question, response, response_duration, overall_score, evaluated_at
                FROM interview_exchanges 
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (test_session_id,))
            
            exchange = cursor.fetchone()
            
            if exchange:
                question, response, duration, score, evaluated = exchange
                print(f"✅ EXCHANGE FOUND IN DATABASE:")
                print(f"   Question: {question[:50]}...")
                print(f"   Response: {response[:50]}...")
                print(f"   Duration: {duration}s")
                print(f"   Score: {score or 0}/10")
                print(f"   Evaluated: {'Yes' if evaluated else 'Processing...'}")
                
                print(f"\n🎉 RECORDING FUNCTION IS WORKING!")
                return True
            else:
                print(f"❌ NO EXCHANGE FOUND IN DATABASE")
                print(f"❌ RECORDING FUNCTION NOT WORKING PROPERLY")
                return False
                
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False

if __name__ == "__main__":
    """Run the test"""
    
    print("🔧 RECORD CANDIDATE RESPONSE - FUNCTION TEST")
    print("=" * 60)
    
    # Run the test
    result = asyncio.run(test_recording_function())
    
    if result:
        print(f"\n✅ SUCCESS: Recording function is working properly!")
        print(f"✅ The interview agent should now record conversations")
        print(f"✅ Try running another interview - exchanges should be saved")
    else:
        print(f"\n❌ FAILURE: Recording function has issues")
        print(f"❌ Need to debug the recording system")
    
    print("=" * 60)
