"""
Database Schema Fix for Automated Evaluation System
Updates the database schema to support all automated evaluation features
"""

import sqlite3
import os
from datetime import datetime

def fix_database_schema():
    """Fix database schema to support automated evaluation system"""
    print("🔧 DATABASE SCHEMA FIX: Updating schema for automated evaluation...")
    print("=" * 70)
    
    os.makedirs("database", exist_ok=True)
    db_path = os.path.join("database", "interview_evaluations.db")
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Get existing columns for interview_sessions table
            cursor = conn.execute("PRAGMA table_info(interview_sessions)")
            existing_session_columns = [row[1] for row in cursor.fetchall()]
            print(f"📊 Existing session columns: {len(existing_session_columns)}")
            
            # Add missing columns to interview_sessions table
            session_columns_to_add = [
                ("overall_score", "REAL DEFAULT 0"),
                ("updated_at", "TEXT")
            ]
            
            for column_name, column_def in session_columns_to_add:
                if column_name not in existing_session_columns:
                    try:
                        conn.execute(f"ALTER TABLE interview_sessions ADD COLUMN {column_name} {column_def}")
                        print(f"✅ Added column: interview_sessions.{column_name}")
                    except Exception as e:
                        if "duplicate column name" not in str(e).lower():
                            print(f"⚠️ Column {column_name}: {e}")
                else:
                    print(f"✅ Column already exists: interview_sessions.{column_name}")
            
            # Get existing columns for interview_exchanges table
            cursor = conn.execute("PRAGMA table_info(interview_exchanges)")
            existing_exchange_columns = [row[1] for row in cursor.fetchall()]
            print(f"📊 Existing exchange columns: {len(existing_exchange_columns)}")
            
            # Add missing columns to interview_exchanges table
            exchange_columns_to_add = [
                ("overall_assessment", "TEXT"),
                ("overall_score", "REAL DEFAULT 0"),
                ("evaluated_at", "TEXT"),
                ("processing_time", "REAL DEFAULT 0")
            ]
            
            for column_name, column_def in exchange_columns_to_add:
                if column_name not in existing_exchange_columns:
                    try:
                        conn.execute(f"ALTER TABLE interview_exchanges ADD COLUMN {column_name} {column_def}")
                        print(f"✅ Added column: interview_exchanges.{column_name}")
                    except Exception as e:
                        if "duplicate column name" not in str(e).lower():
                            print(f"⚠️ Column {column_name}: {e}")
                else:
                    print(f"✅ Column already exists: interview_exchanges.{column_name}")
            
            # Verify the schema
            cursor = conn.execute("PRAGMA table_info(interview_sessions)")
            final_session_columns = [row[1] for row in cursor.fetchall()]
            
            cursor = conn.execute("PRAGMA table_info(interview_exchanges)")
            final_exchange_columns = [row[1] for row in cursor.fetchall()]
            
            print(f"\n📋 FINAL SCHEMA VERIFICATION:")
            print(f"✅ interview_sessions: {len(final_session_columns)} columns")
            print(f"✅ interview_exchanges: {len(final_exchange_columns)} columns")
            
            # Check for required evaluation columns
            required_exchange_columns = [
                'correctness_score', 'completeness_score', 'clarity_score',
                'skill_relevance_score', 'fluency_score', 'confidence_score',
                'sentiment_positive', 'sentiment_neutral', 'sentiment_negative',
                'overall_assessment', 'overall_score', 'evaluated_at'
            ]
            
            missing_columns = [col for col in required_exchange_columns if col not in final_exchange_columns]
            
            if missing_columns:
                print(f"⚠️ Missing columns: {missing_columns}")
                return False
            else:
                print(f"✅ All required evaluation columns present")
            
            conn.commit()
            print(f"✅ Database schema successfully updated!")
            return True
            
    except Exception as e:
        print(f"❌ Database schema fix failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schema_compatibility():
    """Test if the schema works with automated evaluation system"""
    print(f"\n🧪 TESTING SCHEMA COMPATIBILITY...")
    print("=" * 70)
    
    try:
        from automated_evaluation_system import AutomatedEvaluationSystem
        
        # Initialize evaluation system
        evaluator = AutomatedEvaluationSystem(os.getenv("GOOGLE_API_KEY"))
        
        # Test session ID
        test_session_id = f"schema_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Test data storage
        print(f"📝 Testing with session: {test_session_id}")
        
        # Queue a test evaluation
        evaluator.queue_evaluation(
            session_id=test_session_id,
            question="Test question for schema compatibility",
            response="Test response to verify the automated evaluation system works with the updated database schema.",
            response_duration=10.0,
            candidate_name="Schema Test User",
            position="Test Position"
        )
        
        print(f"✅ Queued test evaluation")
        
        # Wait for processing
        import time
        time.sleep(3)
        
        # Try to get summary
        summary = evaluator.get_session_summary(test_session_id)
        
        if "error" in summary:
            print(f"❌ Schema test failed: {summary['error']}")
            return False
        else:
            print(f"✅ Schema test passed!")
            print(f"   Session ID: {summary['session_id']}")
            print(f"   Exchanges: {len(summary['exchanges'])}")
            if summary['exchanges']:
                ex = summary['exchanges'][0]
                print(f"   Sample evaluation: Overall {ex['overall_score']}/10")
                print(f"   Evaluated: {'Yes' if ex['evaluated_at'] else 'No'}")
            return True
            
        # Stop the evaluator worker
        evaluator.stop_evaluation_worker()
        
    except Exception as e:
        print(f"❌ Schema compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_database_status():
    """Show current database status"""
    print(f"\n📊 DATABASE STATUS SUMMARY:")
    print("=" * 70)
    
    try:
        db_path = os.path.join("database", "interview_evaluations.db")
        with sqlite3.connect(db_path) as conn:
            # Session stats
            cursor = conn.execute("SELECT COUNT(*) FROM interview_sessions")
            session_count = cursor.fetchone()[0]
            
            # Exchange stats
            cursor = conn.execute("SELECT COUNT(*) FROM interview_exchanges")
            exchange_count = cursor.fetchone()[0]
            
            # Evaluated exchange stats
            cursor = conn.execute("SELECT COUNT(*) FROM interview_exchanges WHERE evaluated_at IS NOT NULL")
            evaluated_count = cursor.fetchone()[0]
            
            print(f"📈 Total Sessions: {session_count}")
            print(f"📈 Total Exchanges: {exchange_count}")
            print(f"📈 Evaluated Exchanges: {evaluated_count}")
            print(f"📈 Evaluation Coverage: {(evaluated_count/exchange_count*100):.1f}%" if exchange_count > 0 else "📈 Evaluation Coverage: 0%")
            
            return True
            
    except Exception as e:
        print(f"❌ Database status check failed: {e}")
        return False

if __name__ == "__main__":
    """Run database schema fix and verification"""
    
    print("🔧 AUTOMATED EVALUATION SYSTEM - DATABASE SCHEMA FIX")
    print("=" * 70)
    
    # Step 1: Fix database schema
    if not fix_database_schema():
        print("❌ Schema fix failed. Cannot proceed.")
        exit(1)
    
    # Step 2: Test schema compatibility
    if not test_schema_compatibility():
        print("❌ Schema compatibility test failed.")
        exit(1)
    
    # Step 3: Show final status
    show_database_status()
    
    print("\n🎉 DATABASE SCHEMA FIX COMPLETED!")
    print("=" * 70)
    print("✅ Database schema updated for automated evaluation")
    print("✅ Schema compatibility verified")
    print("✅ System ready for automated interviews")
    print("\n🚀 NEXT STEPS:")
    print("   1. Run your LiveKit interview")
    print("   2. System will automatically evaluate each Q&A")
    print("   3. Check database for complete results after interview")
    print("   4. No manual intervention needed!")
    
    print("=" * 70)
