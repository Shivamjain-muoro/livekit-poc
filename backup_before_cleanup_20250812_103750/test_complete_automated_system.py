"""
Complete Automated Evaluation System Test
Creates session, processes evaluations, and verifies everything works end-to-end
"""

import sqlite3
import os
import time
from datetime import datetime
from automated_evaluation_system import get_automated_evaluator

def create_test_session(session_id):
    """Create a test session in the database"""
    try:
        db_path = os.path.join("database", "interview_evaluations.db")
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO interview_sessions (
                    session_id, candidate_name, position, start_time, status
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                "Test Candidate",
                "Backend Developer",
                datetime.now().isoformat(),
                "active"
            ))
            conn.commit()
            print(f"✅ Created test session: {session_id}")
            return True
    except Exception as e:
        print(f"❌ Failed to create test session: {e}")
        return False

def run_complete_test():
    """Run complete automated evaluation test"""
    print("🚀 COMPLETE AUTOMATED EVALUATION SYSTEM TEST")
    print("=" * 70)
    
    # Test session ID
    test_session_id = f"complete_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Step 1: Create session
    if not create_test_session(test_session_id):
        return False
    
    # Step 2: Initialize evaluator
    google_api_key = os.getenv("GOOGLE_API_KEY")
    evaluator = get_automated_evaluator(google_api_key)
    
    # Step 3: Queue multiple evaluations
    test_exchanges = [
        {
            "question": "Tell me about your Python experience and frameworks you've used",
            "response": "I have 4 years of experience with Python. I've worked extensively with Django for web development, Flask for APIs, and FastAPI for microservices. I'm also experienced with SQLAlchemy for database ORM, Celery for background tasks, and pytest for testing.",
            "duration": 42.0
        },
        {
            "question": "Describe a challenging technical problem you solved recently",
            "response": "I optimized a slow database query that was causing timeouts. The original query had multiple nested joins and was taking 8 seconds. I analyzed the execution plan, added proper indexes, restructured the query with CTEs, and implemented Redis caching. This reduced the response time to under 200ms.",
            "duration": 55.0
        },
        {
            "question": "How do you approach code reviews and maintain code quality?",
            "response": "I focus on readability, maintainability, and following coding standards. I check for proper error handling, test coverage, and documentation. I also look for potential security issues and performance bottlenecks. I provide constructive feedback and suggest improvements rather than just pointing out problems.",
            "duration": 38.0
        }
    ]
    
    print(f"📝 Processing {len(test_exchanges)} Q&A exchanges...")
    
    # Queue all evaluations
    for i, exchange in enumerate(test_exchanges, 1):
        print(f"\n🔄 Queuing Exchange {i}:")
        print(f"   Q: {exchange['question'][:60]}...")
        print(f"   A: {exchange['response'][:60]}...")
        
        evaluator.queue_evaluation(
            session_id=test_session_id,
            question=exchange['question'],
            response=exchange['response'],
            response_duration=exchange['duration'],
            candidate_name="Test Candidate",
            position="Backend Developer"
        )
        print(f"   ✅ Queued for automated evaluation")
    
    # Wait for processing
    print(f"\n⏳ Waiting for automated evaluations to complete...")
    time.sleep(10)  # Give more time for processing
    
    # Step 4: Verify results
    print(f"\n📊 VERIFICATION: Checking automated evaluation results...")
    
    # Check database directly
    db_path = os.path.join("database", "interview_evaluations.db")
    try:
        with sqlite3.connect(db_path) as conn:
            # Check session
            cursor = conn.execute("""
                SELECT session_id, candidate_name, overall_score, technical_score, 
                       communication_score, total_questions
                FROM interview_sessions WHERE session_id = ?
            """, (test_session_id,))
            
            session_data = cursor.fetchone()
            if session_data:
                print(f"✅ Session found: {session_data[0]}")
                print(f"   Candidate: {session_data[1]}")
                print(f"   Overall Score: {session_data[2] or 0:.1f}/10")
                print(f"   Technical Score: {session_data[3] or 0:.1f}/10")
                print(f"   Communication Score: {session_data[4] or 0:.1f}/10")
                print(f"   Total Questions: {session_data[5] or 0}")
            else:
                print(f"❌ Session not found in database")
                return False
            
            # Check exchanges
            cursor = conn.execute("""
                SELECT question, response, overall_score, correctness_score, 
                       clarity_score, evaluated_at
                FROM interview_exchanges 
                WHERE session_id = ?
                ORDER BY timestamp
            """, (test_session_id,))
            
            exchanges = cursor.fetchall()
            print(f"\n📋 Found {len(exchanges)} exchanges:")
            
            for i, exchange in enumerate(exchanges, 1):
                question, response, overall_score, correctness, clarity, evaluated = exchange
                print(f"\n   Exchange {i}:")
                print(f"   Question: {question[:50]}...")
                print(f"   Response: {response[:50]}...")
                print(f"   Overall Score: {overall_score or 0:.1f}/10")
                print(f"   Technical Score: {correctness or 0:.1f}/10")
                print(f"   Communication Score: {clarity or 0:.1f}/10")
                print(f"   Evaluated: {'✅ Yes' if evaluated else '❌ No'}")
            
            if len(exchanges) == len(test_exchanges):
                print(f"\n✅ All {len(test_exchanges)} exchanges processed successfully!")
                
                # Check if all are evaluated
                evaluated_count = sum(1 for ex in exchanges if ex[5])  # evaluated_at is not None
                print(f"✅ Evaluated exchanges: {evaluated_count}/{len(exchanges)}")
                
                if evaluated_count == len(exchanges):
                    print(f"🎉 AUTOMATED EVALUATION SYSTEM: FULLY WORKING!")
                    return True
                else:
                    print(f"⚠️ Some exchanges not yet evaluated")
                    return False
            else:
                print(f"❌ Expected {len(test_exchanges)} exchanges, found {len(exchanges)}")
                return False
                
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Stop the evaluator worker
        evaluator.stop_evaluation_worker()

def show_system_summary():
    """Show final system summary"""
    print(f"\n🎯 AUTOMATED EVALUATION SYSTEM SUMMARY:")
    print("=" * 70)
    
    try:
        db_path = os.path.join("database", "interview_evaluations.db")
        with sqlite3.connect(db_path) as conn:
            # Total stats
            cursor = conn.execute("SELECT COUNT(*) FROM interview_sessions")
            total_sessions = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM interview_exchanges")
            total_exchanges = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM interview_exchanges WHERE evaluated_at IS NOT NULL")
            evaluated_exchanges = cursor.fetchone()[0]
            
            print(f"📊 Database Statistics:")
            print(f"   Total Sessions: {total_sessions}")
            print(f"   Total Exchanges: {total_exchanges}")
            print(f"   Evaluated Exchanges: {evaluated_exchanges}")
            print(f"   Evaluation Rate: {(evaluated_exchanges/total_exchanges*100):.1f}%" if total_exchanges > 0 else "   Evaluation Rate: 0%")
            
            # Recent test sessions
            cursor = conn.execute("""
                SELECT session_id, candidate_name, overall_score, total_questions
                FROM interview_sessions 
                WHERE session_id LIKE '%test%'
                ORDER BY start_time DESC 
                LIMIT 3
            """)
            
            test_sessions = cursor.fetchall()
            if test_sessions:
                print(f"\n📋 Recent Test Sessions:")
                for session in test_sessions:
                    session_id, name, score, questions = session
                    print(f"   {session_id} | Score: {score or 0:.1f}/10 | Questions: {questions or 0}")
            
    except Exception as e:
        print(f"❌ Summary generation failed: {e}")

if __name__ == "__main__":
    """Run complete test and show results"""
    
    # Run the complete test
    success = run_complete_test()
    
    # Show system summary
    show_system_summary()
    
    # Final result
    print("\n" + "=" * 70)
    if success:
        print("🎉 SUCCESS: AUTOMATED EVALUATION SYSTEM IS FULLY WORKING!")
        print("✅ System ready for live interviews")
        print("✅ All Q&A exchanges will be automatically evaluated")
        print("✅ Scores saved to database in real-time")
        print("✅ No manual intervention required")
        print("\n🚀 TO USE THE SYSTEM:")
        print("   1. Start your LiveKit interview session")
        print("   2. Conduct normal interview conversation")
        print("   3. System automatically evaluates each Q&A exchange")
        print("   4. After interview, check database for complete results")
        print("   5. All evaluation scores will be available immediately")
    else:
        print("❌ SYSTEM NOT READY: Issues detected in automated evaluation")
        print("❌ Please review the errors above and fix them")
    
    print("=" * 70)
