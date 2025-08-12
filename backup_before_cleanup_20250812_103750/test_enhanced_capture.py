#!/usr/bin/env python3
"""
Test the enhanced interview agent with improved data capture
"""

import asyncio
import sys
import os

# Add the project directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from realtime_interview_tools import start_interview_session, record_candidate_response, end_interview_session

async def test_enhanced_capture():
    """Test the enhanced interview data capture"""
    
    print("🧪 TESTING ENHANCED INTERVIEW DATA CAPTURE")
    print("=" * 50)
    
    # Start a test session
    print("1. 🚀 Starting test session...")
    session_result = await start_interview_session(
        context=None,
        candidate_name="Test Candidate Enhanced",
        position="Software Engineer",
        session_id="test_enhanced_capture"
    )
    print(f"   ✅ Session started: {session_result}")
    
    # Simulate Q&A exchanges
    exchanges = [
        {
            "question": "Tell me about your background in software development.",
            "response": "I have 5 years of experience building web applications with Python and JavaScript. I've worked on e-commerce platforms, data analytics tools, and recently AI-powered applications.",
            "duration": 15.2
        },
        {
            "question": "Describe a challenging technical problem you solved recently.",
            "response": "I optimized a database query that was causing timeouts. I analyzed the execution plan, added proper indexes, and restructured the query to reduce complexity from O(n²) to O(n log n).",
            "duration": 22.8
        },
        {
            "question": "How do you stay updated with new technologies?",
            "response": "I follow tech blogs, contribute to open source projects, attend virtual conferences, and practice with side projects. I recently learned about WebRTC for real-time applications.",
            "duration": 18.5
        },
        {
            "question": "What interests you about this position?",
            "response": "I'm excited about working on AI-powered interview systems. The combination of real-time processing, natural language understanding, and user experience optimization aligns perfectly with my interests.",
            "duration": 19.3
        }
    ]
    
    print(f"\n2. 💬 Recording {len(exchanges)} Q&A exchanges...")
    
    for i, exchange in enumerate(exchanges, 1):
        print(f"   📝 Recording exchange {i}...")
        
        result = await record_candidate_response(
            context=None,
            session_id="test_enhanced_capture",
            question=exchange["question"],
            response=exchange["response"],
            response_duration=exchange["duration"]
        )
        
        print(f"   ✅ Exchange {i} recorded: {result[:80]}...")
    
    # End the session
    print(f"\n3. 🏁 Ending test session...")
    end_result = await end_interview_session(
        context=None,
        session_id="test_enhanced_capture"
    )
    print(f"   ✅ Session ended: {end_result}")
    
    print(f"\n✅ ENHANCED CAPTURE TEST COMPLETE!")
    print(f"📊 Now you can use: python evaluate_interview_session.py")
    print(f"🔍 Look for session: test_enhanced_capture")

if __name__ == "__main__":
    asyncio.run(test_enhanced_capture())
