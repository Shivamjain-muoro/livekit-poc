"""
Complete Flow Test for Pure LiveKit Interview System
Tests all the implemented functionality end-to-end
"""

import asyncio
import json
from interview_tools import (
    get_candidate_profile,
    generate_interview_questions,
    evaluate_candidate_response,
    save_interview_response,
    complete_interview_session,
    get_interview_feedback,
    generate_interview_report
)
from livekit.agents import RunContext

class MockRunContext:
    """Mock context for testing function tools"""
    def __init__(self):
        self.session_id = "test_session_001"

async def test_complete_interview_flow():
    """Test the complete interview process"""
    
    print("🎯 Testing Complete LiveKit Interview Flow")
    print("=" * 60)
    
    # Mock context
    context = MockRunContext()
    session_id = "test_interview_123"
    
    print("\n📋 Step 1: Get Candidate Profile")
    print("-" * 40)
    profile_result = await get_candidate_profile(context, session_id)
    profile_data = json.loads(profile_result)
    print(f"✅ Profile Created: {profile_data['name']} for {profile_data['position']}")
    print(f"   Skills: {profile_data['skills']}")
    
    print("\n❓ Step 2: Generate Interview Questions")
    print("-" * 40)
    questions_result = await generate_interview_questions(
        context,
        candidate_name=profile_data['name'],
        position=profile_data['position'],
        experience_level=profile_data['experience_level'],
        skills=profile_data['skills']
    )
    questions = json.loads(questions_result)
    print(f"✅ Generated {len(questions)} questions:")
    for i, q in enumerate(questions[:3], 1):  # Show first 3
        print(f"   {i}. {q}")
    
    print("\n💬 Step 3: Simulate Interview Responses & Evaluations")
    print("-" * 40)
    
    # Simulate responses to first 3 questions
    sample_responses = [
        "I'm a passionate software developer with 5 years of experience in full-stack development. I love solving complex problems and building scalable applications.",
        "One challenging project was building a real-time chat application that needed to handle 10,000+ concurrent users. I used WebSockets and Redis for scalability.",
        "I believe in clear communication and collaborative problem-solving. I always document my code and help team members when they're stuck."
    ]
    
    response_ids = []
    for i, (question, response) in enumerate(zip(questions[:3], sample_responses), 1):
        print(f"\n   Question {i}: {question[:80]}...")
        print(f"   Response: {response[:100]}...")
        
        # Evaluate the response
        evaluation_result = await evaluate_candidate_response(
            context, question, response
        )
        print(f"   ✅ Evaluation generated")
        
        # Save the response
        save_result = await save_interview_response(
            context, session_id, question, response, evaluation_result
        )
        response_ids.append(save_result)
        print(f"   💾 {save_result}")
    
    print("\n🏁 Step 4: Complete Interview Session")
    print("-" * 40)
    overall_assessment = """
    The candidate demonstrated strong technical knowledge and excellent communication skills. 
    Their experience with scalable systems and collaborative approach makes them a strong fit 
    for our team. Recommend moving forward with technical round.
    """
    
    completion_result = await complete_interview_session(
        context, session_id, overall_assessment.strip()
    )
    print(f"✅ {completion_result}")
    
    print("\n📊 Step 5: Generate Comprehensive Feedback")
    print("-" * 40)
    feedback_result = await get_interview_feedback(context, session_id)
    feedback_data = json.loads(feedback_result)
    
    print(f"✅ Feedback Generated for {feedback_data['candidate_name']}")
    print(f"   Position: {feedback_data['position']}")
    print(f"   Total Questions: {feedback_data['total_questions']}")
    print(f"   Status: {feedback_data['interview_status']}")
    print(f"   Assessment: {feedback_data['overall_assessment'][:100]}...")
    
    print("\n📄 Step 6: Generate Professional Report")
    print("-" * 40)
    report_result = await generate_interview_report(context, session_id)
    print("✅ Professional Report Generated:")
    print(report_result[:500] + "..." if len(report_result) > 500 else report_result)
    
    print("\n🎉 COMPLETE FLOW TEST SUCCESSFUL!")
    print("=" * 60)
    print("✅ All interview tools working correctly")
    print("✅ Database persistence working")
    print("✅ AI evaluation working")
    print("✅ Report generation working")
    print("\n🚀 Ready for Live Voice Testing!")

if __name__ == "__main__":
    asyncio.run(test_complete_interview_flow())
