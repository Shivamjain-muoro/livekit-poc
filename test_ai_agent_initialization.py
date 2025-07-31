#!/usr/bin/env python3
"""
Test AI Agent Initialization
Test if the AI agent is properly initializing after session creation
"""

import asyncio
import aiohttp
import json
import time

async def test_ai_agent_init():
    """Test the complete AI agent initialization flow"""
    
    print("🧪 Testing AI Agent Initialization...")
    
    # Test session creation
    session_data = {
        "candidate": {
            "name": "Test User",
            "email": "test@example.com",
            "position": "Software Engineer",
            "experience_level": "mid",
            "skills": ["Python", "JavaScript", "React"]
        },
        "interview_type": "technical",
        "max_questions": 5,
        "enable_real_time_feedback": True
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Create session
            print("📡 Creating interview session...")
            async with session.post(
                'http://localhost:8001/api/voice-interview/create',
                json=session_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ Session creation failed: {response.status} - {error_text}")
                    return
                
                session_info = await response.json()
                session_id = session_info['session_id']
                print(f"✅ Session created: {session_id}")
                print(f"🏠 Room: {session_info['room_name']}")
                print(f"🔧 Fallback mode: {session_info['fallback_mode']}")
            
            # Wait a moment for initialization
            print("⏳ Waiting for AI agent initialization...")
            await asyncio.sleep(3)
            
            # Check status multiple times to see the progression
            for check_num in range(1, 6):
                print(f"\n📊 Status check #{check_num}:")
                
                async with session.get(f'http://localhost:8001/api/voice-interview/status/{session_id}') as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"❌ Status check failed: {response.status} - {error_text}")
                        continue
                    
                    status = await response.json()
                    print(f"   Status: {status['status']}")
                    print(f"   AI Agent Connected: {status['ai_agent_connected']}")
                    print(f"   Question: {status['current_question']} / {status['total_questions']}")
                    print(f"   Fallback Mode: {status['fallback_mode']}")
                    print(f"   Start Time: {status.get('start_time', 'Not started')}")
                    
                    if status['ai_agent_connected'] and status['status'] != 'created':
                        print("✅ AI Agent is working!")
                        break
                
                if check_num < 5:
                    await asyncio.sleep(4)
            
            # Clean up
            print(f"\n🧹 Cleaning up session {session_id}...")
            async with session.delete(f'http://localhost:8001/api/voice-interview/{session_id}') as response:
                if response.status == 200:
                    print("✅ Session cleaned up successfully")
                else:
                    print(f"⚠️ Cleanup warning: {response.status}")
                    
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_agent_init())
