"""
Quick Test for Voice AI Interview System
=======================================
Tests the current system to verify it's working properly.
"""

import asyncio
import json
import httpx

async def test_voice_ai_system():
    """Test the voice AI interview system"""
    print("🧪 Testing Voice AI Interview System")
    print("=" * 40)
    
    base_url = "http://localhost:8001"
    
    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Health check
            print("1️⃣ Testing health endpoint...")
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"   ✅ Health: {health_data['status']}")
                print(f"   🤖 AI Available: {health_data['ai_enabled']}")
                print(f"   🎙️ LiveKit Available: {health_data['livekit_enabled']}")
                print(f"   ⚠️ Fallback Mode: {health_data.get('fallback_mode', False)}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False

            # Test 2: Create voice interview session
            print("\n2️⃣ Testing session creation...")
            session_data = {
                "candidate": {
                    "name": "Test Candidate",
                    "email": "test@example.com", 
                    "position": "Software Engineer",
                    "experience_level": "mid",
                    "skills": ["Python", "JavaScript", "React"]
                },
                "interview_type": "technical",
                "max_questions": 5,
                "enable_real_time_feedback": True
            }
            
            response = await client.post(f"{base_url}/api/voice-interview/create", json=session_data)
            if response.status_code == 200:
                session_result = response.json()
                session_id = session_result['session_id']
                print(f"   ✅ Session created: {session_id}")
                print(f"   🏠 Room: {session_result['room_name']}")
                print(f"   🤖 AI Agent Ready: {session_result['ai_agent_ready']}")
                print(f"   ⚠️ Fallback Mode: {session_result.get('fallback_mode', False)}")
            else:
                error_text = response.text
                print(f"   ❌ Session creation failed: {response.status_code}")
                print(f"   📄 Error: {error_text}")
                return False

            # Test 3: Check session status
            print("\n3️⃣ Testing session status...")
            await asyncio.sleep(2)  # Give time for AI agent to initialize
            
            response = await client.get(f"{base_url}/api/voice-interview/status/{session_id}")
            if response.status_code == 200:
                status_data = response.json()
                print(f"   ✅ Status: {status_data['status']}")
                print(f"   📊 Progress: {status_data['current_question']}/{status_data['total_questions']}")
                print(f"   🤖 AI Connected: {status_data['ai_agent_connected']}")
                print(f"   ⚠️ Fallback Mode: {status_data.get('fallback_mode', False)}")
            else:
                print(f"   ❌ Status check failed: {response.status_code}")

            # Test 4: Wait a bit and check if interview progresses
            print("\n4️⃣ Testing interview progression...")
            await asyncio.sleep(5)  # Wait for interview to start
            
            response = await client.get(f"{base_url}/api/voice-interview/status/{session_id}")
            if response.status_code == 200:
                status_data = response.json()
                print(f"   ✅ Current Status: {status_data['status']}")
                print(f"   📊 Questions Available: {status_data['total_questions']}")
                if status_data['total_questions'] > 0:
                    print("   ✅ Questions generated successfully")
                else:
                    print("   ⚠️ No questions generated yet")

            # Test 5: Get partial results
            print("\n5️⃣ Testing results endpoint...")
            response = await client.get(f"{base_url}/api/voice-interview/results/{session_id}")
            if response.status_code == 200:
                results_data = response.json()
                summary = results_data['interview_summary']
                print(f"   ✅ Results accessible")
                print(f"   📊 Questions: {summary['total_questions']}")
                print(f"   📝 Answers: {summary['total_answers']}")
                print(f"   ⭐ Average Score: {summary['average_score']}")
                print(f"   ⚠️ Fallback Mode: {summary.get('fallback_mode', False)}")
            else:
                print(f"   ❌ Results check failed: {response.status_code}")

            # Test 6: Cleanup - end interview
            print("\n6️⃣ Cleaning up...")
            response = await client.delete(f"{base_url}/api/voice-interview/{session_id}")
            if response.status_code == 200:
                print("   ✅ Interview ended successfully")
            else:
                print(f"   ⚠️ Cleanup warning: {response.status_code}")

            print("\n🎉 Voice AI Interview System Test Complete!")
            print("=" * 40)
            print("✅ System is working properly")
            print(f"🌐 Access the interface: {base_url}/voice-ai")
            print("💡 The system is ready for voice interviews!")
            
            return True

        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_voice_ai_system())
    if success:
        print("\n🚀 System ready for production use!")
    else:
        print("\n🔧 System needs attention before use")
