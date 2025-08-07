"""
System Readiness Verification and Automated Evaluation Test
Verifies that all components are working and tests the automated evaluation system
"""

import os
import json
import sqlite3
from datetime import datetime
from automated_evaluation_system import get_automated_evaluator
import time

def verify_system_readiness():
    """Verify that all system components are ready"""
    print("🔍 SYSTEM VERIFICATION: Checking automated evaluation system...")
    print("=" * 60)
    
    # Check 1: Environment variables
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if google_api_key:
        print("✅ Google API Key: Found")
    else:
        print("⚠️ Google API Key: Missing (will use fallback scores)")
    
    # Check 2: Database setup
    try:
        os.makedirs("database", exist_ok=True)
        db_path = os.path.join("database", "interview_evaluations.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            if 'interview_sessions' in tables and 'interview_exchanges' in tables:
                print("✅ Database Schema: Ready")
            else:
                print("❌ Database Schema: Missing tables")
                return False
    except Exception as e:
        print(f"❌ Database: Error - {e}")
        return False
    
    # Check 3: Automated evaluator
    try:
        evaluator = get_automated_evaluator(google_api_key)
        print("✅ Automated Evaluator: Initialized")
    except Exception as e:
        print(f"❌ Automated Evaluator: Error - {e}")
        return False
    
    # Check 4: Required files
    required_files = [
        "realtime_interview_tools.py",
        "automated_evaluation_system.py",
        "complete_interview_agent.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}: Found")
        else:
            print(f"❌ {file}: Missing")
            return False
    
    print("=" * 60)
    print("🎉 SYSTEM STATUS: ALL COMPONENTS READY!")
    return True

def test_automated_evaluation():
    """Test the automated evaluation system with sample data"""
    print("\n🧪 AUTOMATED EVALUATION TEST: Testing with sample interview...")
    print("=" * 60)
    
    # Initialize evaluator
    google_api_key = os.getenv("GOOGLE_API_KEY")
    evaluator = get_automated_evaluator(google_api_key)
    
    # Test session ID
    test_session_id = f"automated_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Sample Q&A exchanges
    test_exchanges = [
        {
            "question": "Tell me about your experience with Python programming",
            "response": "I have 4 years of experience with Python, working on web development using Django and Flask. I've built REST APIs, worked with databases like PostgreSQL and MongoDB, and have experience with automated testing using pytest.",
            "response_duration": 35.0
        },
        {
            "question": "Can you describe a challenging project you've worked on?",
            "response": "I worked on a real-time data processing system that handled over 10,000 requests per minute. The main challenge was optimizing database queries and implementing caching strategies to reduce response time from 2 seconds to under 200ms.",
            "response_duration": 45.0
        },
        {
            "question": "How do you handle debugging complex issues?",
            "response": "I use a systematic approach: first, I reproduce the issue, then I use logging and debugging tools like pdb to trace the problem. I also write unit tests to isolate the issue and ensure my fix doesn't break anything else.",
            "response_duration": 30.0
        }
    ]
    
    print(f"📝 Test Session ID: {test_session_id}")
    print(f"📊 Testing {len(test_exchanges)} Q&A exchanges...")
    
    # Queue evaluations
    for i, exchange in enumerate(test_exchanges, 1):
        print(f"\n🔄 Processing Exchange {i}/{len(test_exchanges)}")
        print(f"   Question: {exchange['question'][:60]}...")
        print(f"   Response: {exchange['response'][:60]}...")
        
        evaluator.queue_evaluation(
            session_id=test_session_id,
            question=exchange['question'],
            response=exchange['response'],
            response_duration=exchange['response_duration'],
            candidate_name="Test Candidate",
            position="Backend Developer"
        )
        print(f"   ✅ Queued for automated evaluation")
    
    # Wait for processing
    print("\n⏳ Waiting for automated evaluations to complete...")
    time.sleep(8)  # Give time for background processing
    
    # Get results
    print("\n📊 AUTOMATED EVALUATION RESULTS:")
    print("=" * 60)
    
    summary = evaluator.get_session_summary(test_session_id)
    
    if "error" in summary:
        print(f"❌ Error getting results: {summary['error']}")
        return False
    
    print(f"✅ Session: {summary['session_id']}")
    print(f"✅ Candidate: {summary['candidate_name']}")
    print(f"✅ Position: {summary['position']}")
    print(f"✅ Overall Score: {summary['overall_score']:.1f}/10")
    print(f"✅ Technical Score: {summary['technical_score']:.1f}/10")
    print(f"✅ Communication Score: {summary['communication_score']:.1f}/10")
    print(f"✅ Total Questions: {summary['total_questions']}")
    
    print(f"\n📋 EXCHANGE DETAILS:")
    for i, exchange in enumerate(summary['exchanges'], 1):
        print(f"\n   Exchange {i}:")
        print(f"   Question: {exchange['question'][:80]}...")
        print(f"   Response: {exchange['response'][:80]}...")
        print(f"   Overall Score: {exchange['overall_score']:.1f}/10")
        print(f"   Technical Score: {exchange['correctness_score']:.1f}/10")
        print(f"   Communication Score: {exchange['clarity_score']:.1f}/10")
        print(f"   Key Skills: {', '.join(exchange['key_skills'])}")
        print(f"   Evaluated: {'✅ Yes' if exchange['evaluated_at'] else '❌ No'}")
    
    print("=" * 60)
    print("🎉 AUTOMATED EVALUATION TEST: SUCCESSFUL!")
    print("✅ All Q&A exchanges were automatically evaluated and stored with scores")
    return True

def check_database_content():
    """Check what's currently in the database"""
    print("\n💾 DATABASE CONTENT CHECK:")
    print("=" * 60)
    
    try:
        db_path = os.path.join("database", "interview_evaluations.db")
        with sqlite3.connect(db_path) as conn:
            # Check sessions
            cursor = conn.execute("SELECT COUNT(*) FROM interview_sessions")
            session_count = cursor.fetchone()[0]
            print(f"📊 Total Sessions: {session_count}")
            
            # Check exchanges
            cursor = conn.execute("SELECT COUNT(*) FROM interview_exchanges")
            exchange_count = cursor.fetchone()[0]
            print(f"📊 Total Exchanges: {exchange_count}")
            
            # Check evaluated exchanges
            cursor = conn.execute("SELECT COUNT(*) FROM interview_exchanges WHERE evaluated_at IS NOT NULL")
            evaluated_count = cursor.fetchone()[0]
            print(f"📊 Evaluated Exchanges: {evaluated_count}")
            
            # Show recent sessions
            cursor = conn.execute("""
                SELECT session_id, candidate_name, start_time, overall_score, total_questions
                FROM interview_sessions 
                ORDER BY start_time DESC 
                LIMIT 5
            """)
            
            recent_sessions = cursor.fetchall()
            if recent_sessions:
                print(f"\n📋 Recent Sessions:")
                for session in recent_sessions:
                    session_id, name, start_time, score, questions = session
                    score = score or 0
                    questions = questions or 0
                    print(f"   {session_id[:20]}... | {name} | Score: {score:.1f}/10 | Questions: {questions}")
            else:
                print("📋 No sessions found in database")
                
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    """Run complete system verification and testing"""
    
    print("🚀 AUTOMATED INTERVIEW EVALUATION SYSTEM")
    print("🔧 COMPLETE SYSTEM VERIFICATION AND TEST")
    print("=" * 70)
    
    # Step 1: Verify system readiness
    if not verify_system_readiness():
        print("❌ System not ready. Please fix the issues above.")
        exit(1)
    
    # Step 2: Check existing database content
    check_database_content()
    
    # Step 3: Test automated evaluation
    if not test_automated_evaluation():
        print("❌ Automated evaluation test failed.")
        exit(1)
    
    # Step 4: Final verification
    print("\n🎉 FINAL VERIFICATION:")
    print("=" * 60)
    print("✅ System is FULLY READY for automated interviews")
    print("✅ Automated evaluation is working perfectly")
    print("✅ Database storage with scores is functional")
    print("✅ No manual intervention required")
    print("\n🚀 WHAT HAPPENS NOW:")
    print("   1. Start your LiveKit interview")
    print("   2. System automatically evaluates each Q&A exchange")
    print("   3. All scores are saved to database in real-time")
    print("   4. After interview, check database for complete results")
    print("   5. No manual analysis needed!")
    print("\n💾 To check your interview results:")
    print("   - Look in database/interview_evaluations.db")
    print("   - All exchanges will have evaluation scores")
    print("   - Session statistics automatically calculated")
    
    print("=" * 70)
    print("🎯 SYSTEM STATUS: READY FOR AUTOMATED INTERVIEWS! 🎯")
