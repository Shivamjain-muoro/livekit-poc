#!/usr/bin/env python3
"""
Test Session ID Coordination - Verify Q&A Recording Works
"""

import asyncio
import os
import json
from datetime import datetime
from realtime_interview_tools import (
    start_interview_session,
    record_candidate_response,
    get_real_time_progress,
    end_interview_session,
    ACTIVE_SESSIONS
)
from check_db_status import check_database_status

async def test_session_coordination():
    """Test that session ID coordination works end-to-end"""
    
    print("🧪 TESTING SESSION ID COORDINATION")
    print("="*60)
    
    # Test session ID
    test_session_id = f"test_coordination_{datetime.now().strftime('%H%M%S')}"
    
    print(f"📝 Test Session ID: {test_session_id}")
    print()
    
    # 1. Start session
    print("1️⃣ STARTING SESSION...")
    start_result = await start_interview_session(
        context=None,
        candidate_name="Test Candidate Coordination",
        position="Test Position",
        session_id=test_session_id
    )
    print(f"   ✅ Start result: {start_result}")
    print(f"   📊 Active sessions: {list(ACTIVE_SESSIONS.keys())}")
    print()
    
    # 2. Test get_real_time_progress for session ID
    print("2️⃣ GETTING SESSION ID FROM PROGRESS...")
    progress_result = await get_real_time_progress(context=None)
    progress_data = json.loads(progress_result)
    detected_session_id = progress_data.get("session_id")
    print(f"   ✅ Progress result: {progress_result}")
    print(f"   🎯 Detected session ID: {detected_session_id}")
    print()
    
    # 3. Test recording with auto-detected session ID
    print("3️⃣ RECORDING Q&A (AUTO-DETECTED SESSION ID)...")
    record_result1 = await record_candidate_response(
        context=None,
        # session_id=None,  # Let it auto-detect
        question="What is your background in software development?",
        response="I have 4 years of experience as a backend engineer, working on projects like loan management systems and e-commerce platforms.",
        response_duration=15.0
    )
    print(f"   ✅ Record result 1: {record_result1}")
    print()
    
    # 4. Test recording with explicit session ID
    print("4️⃣ RECORDING Q&A (EXPLICIT SESSION ID)...")
    record_result2 = await record_candidate_response(
        context=None,
        session_id=detected_session_id,
        question="Can you tell me about a specific project you worked on?",
        response="I worked on a loan management system that automated the approval process and integrated with multiple banks.",
        response_duration=20.0
    )
    print(f"   ✅ Record result 2: {record_result2}")
    print()
    
    # 5. Test progress after recording
    print("5️⃣ CHECKING PROGRESS AFTER RECORDING...")
    final_progress = await get_real_time_progress(context=None, session_id=detected_session_id)
    final_data = json.loads(final_progress)
    print(f"   ✅ Final progress: {final_progress}")
    print(f"   📊 Q&A Pairs recorded: {final_data.get('questions_asked', 0)}")
    print()
    
    # 6. End session
    print("6️⃣ ENDING SESSION...")
    end_result = await end_interview_session(context=None, session_id=detected_session_id)
    print(f"   ✅ End result: {end_result}")
    print()
    
    # 7. Check database
    print("7️⃣ CHECKING DATABASE...")
    await asyncio.sleep(2)  # Give background threads time to save
    check_database_status()
    print()
    
    # Summary
    print("📊 TEST SUMMARY:")
    print(f"   ✅ Session started: {test_session_id}")
    print(f"   ✅ Session auto-detected: {detected_session_id}")
    print(f"   ✅ Q&A pairs recorded: {final_data.get('questions_asked', 0)}")
    print(f"   ✅ Session coordination: {'WORKING' if final_data.get('questions_asked', 0) >= 2 else 'NEEDS_FIX'}")
    
    return {
        "session_started": test_session_id,
        "session_detected": detected_session_id,
        "qa_pairs_recorded": final_data.get('questions_asked', 0),
        "coordination_working": final_data.get('questions_asked', 0) >= 2
    }

if __name__ == "__main__":
    print("🚀 Starting Session ID Coordination Test...")
    result = asyncio.run(test_session_coordination())
    print(f"\n🎯 FINAL RESULT: {result}")
    
    if result["coordination_working"]:
        print("✅ SUCCESS: Session ID coordination is working!")
        print("✅ The system will now properly save Q&A exchanges to database")
    else:
        print("❌ ISSUE: Session ID coordination needs more work")
        print("❌ Q&A exchanges may not be saved properly")
