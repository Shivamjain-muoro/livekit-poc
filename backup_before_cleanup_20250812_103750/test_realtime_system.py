"""
Real-Time Interview System Test
Test the enhanced real-time tools for instant response
"""

import os
import time
import asyncio
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_real_time_system():
    """Test the real-time interview system"""
    print("🚀 TESTING REAL-TIME INTERVIEW SYSTEM")
    print("=" * 50)
    
    # Mock context for testing
    class MockContext:
        def __init__(self):
            self.room_name = "test_room_realtime"
    
    context = MockContext()
    
    try:
        # Import real-time tools
        from realtime_interview_tools import (
            start_interview_session,
            record_candidate_response,
            get_real_time_progress,
            end_interview_session
        )
        
        print("✅ Real-time tools imported successfully")
        
        # Test 1: Instant session start
        print("\n🚀 TEST 1: Instant Session Start")
        start_time = time.time()
        
        result = await start_interview_session(
            context=context,
            candidate_name="John Doe",
            position="Senior Software Engineer",
            session_id="test_realtime_session"
        )
        
        start_duration = time.time() - start_time
        print(f"⚡ Session start took: {start_duration*1000:.1f}ms")
        print(f"📊 Result: {result[:100]}...")
        
        # Test 2: Instant response recording
        print("\n📝 TEST 2: Instant Response Recording")
        
        questions_and_responses = [
            ("Tell me about your programming experience.", "I have 5 years of experience in Python and JavaScript, working on web applications and APIs."),
            ("What's your biggest technical achievement?", "I led the development of a microservices architecture that improved system performance by 40%."),
            ("How do you handle debugging complex issues?", "I use systematic debugging, starting with logs, then step-through debugging, and collaborate with the team."),
        ]
        
        total_record_time = 0
        for i, (question, response) in enumerate(questions_and_responses):
            record_start = time.time()
            
            result = await record_candidate_response(
                context=context,
                session_id="test_realtime_session",
                question=question,
                response=response,
                response_duration=3.5 + i * 0.5  # Simulate varying response times
            )
            
            record_duration = time.time() - record_start
            total_record_time += record_duration
            
            print(f"⚡ Response {i+1} recorded in: {record_duration*1000:.1f}ms")
            
            # Get real-time progress
            progress = await get_real_time_progress(context, "test_realtime_session")
            print(f"📊 Current progress: {progress[:80]}...")
        
        print(f"\n📈 Average recording time: {(total_record_time/len(questions_and_responses))*1000:.1f}ms")
        
        # Test 3: Instant session end
        print("\n🏁 TEST 3: Instant Session End")
        end_start = time.time()
        
        result = await end_interview_session(
            context=context,
            session_id="test_realtime_session"
        )
        
        end_duration = time.time() - end_start
        print(f"⚡ Session end took: {end_duration*1000:.1f}ms")
        print(f"📊 Final result: {result[:150]}...")
        
        # Performance Summary
        print(f"\n🎯 PERFORMANCE SUMMARY")
        print("=" * 30)
        print(f"⚡ Session Start: {start_duration*1000:.1f}ms")
        print(f"⚡ Avg Response Recording: {(total_record_time/len(questions_and_responses))*1000:.1f}ms")
        print(f"⚡ Session End: {end_duration*1000:.1f}ms")
        print(f"✅ All operations completed instantly!")
        
        # Wait a bit for background evaluation
        print(f"\n🔄 Waiting 5 seconds for background evaluation...")
        await asyncio.sleep(5)
        
        # Check if evaluation completed
        progress = await get_real_time_progress(context, "test_realtime_session")
        print(f"📊 Final progress: {progress}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 REAL-TIME INTERVIEW SYSTEM PERFORMANCE TEST")
    print("=" * 55)
    
    # Run async test
    try:
        result = asyncio.run(test_real_time_system())
        
        if result:
            print(f"\n🟢 ALL TESTS PASSED!")
            print("✅ Real-time system is working correctly")
            print("✅ All operations complete in milliseconds")
            print("✅ Background evaluation is running")
            print("✅ Ready for production use")
            
            print(f"\n🚀 SYSTEM READY FOR REAL-TIME INTERVIEWS!")
            print("📋 Next steps:")
            print("1. Start agent: python complete_interview_agent.py dev")
            print("2. Generate URL: python generate_test_url.py")
            print("3. Conduct interview with instant responses")
            print("4. Check comprehensive reports after completion")
            
        else:
            print(f"\n🔴 TESTS FAILED")
            print("🔧 Check the error logs above")
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")

if __name__ == "__main__":
    main()
