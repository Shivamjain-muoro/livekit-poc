#!/usr/bin/env python3
"""
Test direct database saving for interview exchanges
"""

import sqlite3
import os
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    db_path = os.path.join("database", "interview_evaluations.db")
    return sqlite3.connect(db_path)

def test_direct_save():
    """Test saving Q&A exchanges directly to database"""
    
    print("🔧 TESTING DIRECT DATABASE SAVE")
    print("=" * 40)
    
    session_id = "test_direct_save"
    
    # Test exchanges
    exchanges = [
        {
            "question": "What is your programming experience?",
            "response": "I have 5 years of experience in Python, JavaScript, and SQL.",
            "duration": 12.5
        },
        {
            "question": "Describe a challenging project.",
            "response": "I built a real-time chat application with 10,000+ concurrent users.",
            "duration": 18.7
        }
    ]
    
    try:
        with get_db_connection() as conn:
            # First, create a test session
            print("1. 📝 Creating test session...")
            conn.execute("""
                INSERT OR REPLACE INTO interview_sessions 
                (session_id, candidate_name, position, start_time, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                "Test Candidate Direct",
                "Software Engineer", 
                datetime.now().isoformat(),
                "active"
            ))
            
            # Now save exchanges
            print(f"2. 💾 Saving {len(exchanges)} exchanges...")
            
            for i, exchange in enumerate(exchanges, 1):
                timestamp = datetime.now().isoformat()
                
                print(f"   📝 Saving exchange {i}...")
                conn.execute("""
                    INSERT INTO interview_exchanges 
                    (session_id, question, response, timestamp, response_duration)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    session_id, 
                    exchange["question"],
                    exchange["response"], 
                    timestamp,
                    exchange["duration"]
                ))
                
                print(f"   ✅ Exchange {i} saved successfully")
            
            conn.commit()
            print("✅ All data committed to database")
            
            # Verify the data was saved
            print("3. 🔍 Verifying saved data...")
            cursor = conn.execute("""
                SELECT session_id, question, response, response_duration
                FROM interview_exchanges 
                WHERE session_id = ?
                ORDER BY timestamp
            """, (session_id,))
            
            saved_exchanges = cursor.fetchall()
            print(f"   📊 Found {len(saved_exchanges)} saved exchanges:")
            
            for i, (sid, q, r, d) in enumerate(saved_exchanges, 1):
                print(f"      {i}. Q: {q[:40]}...")
                print(f"         R: {r[:40]}...")
                print(f"         Duration: {d}s")
            
            # Update session to completed
            print("4. 🏁 Completing session...")
            conn.execute("""
                UPDATE interview_sessions 
                SET status = 'completed', end_time = ?
                WHERE session_id = ?
            """, (datetime.now().isoformat(), session_id))
            
            conn.commit()
            print("✅ Session marked as completed")
            
    except Exception as e:
        print(f"❌ Error during direct save test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_save()
    print("\n🎯 Now you can test evaluation with:")
    print("   python evaluate_interview_session.py")
    print("   Look for session: test_direct_save")
