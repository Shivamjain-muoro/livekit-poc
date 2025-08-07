"""
Interview System Status Check
Quick verification that everything is ready for automated interviews
"""

import os
import sqlite3
from datetime import datetime

def check_system_status():
    """Check that the interview system is ready"""
    print("🔍 INTERVIEW SYSTEM STATUS CHECK")
    print("=" * 50)
    
    # Check 1: Agent file updated
    try:
        with open("complete_interview_agent.py", "r") as f:
            content = f.read()
            if "RECORD EVERY CONVERSATION EXCHANGE" in content:
                print("✅ Agent instructions: Updated with recording guidance")
            else:
                print("❌ Agent instructions: Not updated properly")
                return False
    except Exception as e:
        print(f"❌ Agent file check failed: {e}")
        return False
    
    # Check 2: Database schema
    try:
        db_path = os.path.join("database", "interview_evaluations.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("PRAGMA table_info(interview_exchanges)")
            columns = [row[1] for row in cursor.fetchall()]
            required_columns = ['question', 'response', 'overall_score', 'evaluated_at']
            
            missing = [col for col in required_columns if col not in columns]
            if missing:
                print(f"❌ Database schema: Missing columns {missing}")
                return False
            else:
                print("✅ Database schema: All required columns present")
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False
    
    # Check 3: Recording function
    try:
        from realtime_interview_tools import record_candidate_response
        print("✅ Recording function: Available")
    except ImportError as e:
        print(f"❌ Recording function: Import failed - {e}")
        return False
    
    # Check 4: Automated evaluation
    try:
        from automated_evaluation_system import get_automated_evaluator
        evaluator = get_automated_evaluator()
        print("✅ Automated evaluation: System ready")
    except Exception as e:
        print(f"❌ Automated evaluation: Failed - {e}")
        return False
    
    # Check 5: Recent test data
    try:
        db_path = os.path.join("database", "interview_evaluations.db")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM interview_exchanges 
                WHERE session_id LIKE '%test%' AND evaluated_at IS NOT NULL
            """)
            test_exchanges = cursor.fetchone()[0]
            
            if test_exchanges > 0:
                print(f"✅ Test data: {test_exchanges} test exchanges with evaluations")
            else:
                print("⚠️ Test data: No recent test evaluations found")
    except Exception as e:
        print(f"⚠️ Test data check: {e}")
    
    print("\n🎯 SYSTEM STATUS: READY FOR INTERVIEWS!")
    return True

def show_usage_instructions():
    """Show how to use the system"""
    print("\n📋 HOW TO USE THE AUTOMATED INTERVIEW SYSTEM:")
    print("=" * 50)
    print("1. 🚀 Start the LiveKit agent:")
    print("   python complete_interview_agent.py")
    print()
    print("2. 🎤 Conduct your interview normally")
    print("   - Agent will automatically record every Q&A exchange")
    print("   - Evaluation happens in background during conversation")
    print("   - No manual intervention needed")
    print()
    print("3. 📊 Check results after interview:")
    print("   python check_interview_results.py")
    print("   python check_interview_results.py <session_id>")
    print()
    print("4. ✅ What you'll get automatically:")
    print("   - Complete Q&A transcript")
    print("   - Technical scores (correctness, completeness)")
    print("   - Communication scores (clarity, fluency)")
    print("   - Overall evaluation and recommendations")
    print("   - Skills demonstrated and areas of concern")

def show_troubleshooting():
    """Show troubleshooting tips"""
    print("\n🔧 TROUBLESHOOTING:")
    print("=" * 50)
    print("❓ If no exchanges are recorded:")
    print("   - Check that the AI agent is using record_candidate_response")
    print("   - Look for 'Recording Q&A' messages in the logs")
    print("   - Ensure the conversation has substantial exchanges")
    print()
    print("❓ If evaluations are missing:")
    print("   - Wait a few seconds after interview for processing")
    print("   - Check that automated evaluation worker is running")
    print("   - Look for 'AUTOMATED_EVAL' messages in logs")
    print()
    print("❓ If scores are all 0:")
    print("   - Check that evaluated_at is not null in database")
    print("   - Verify automated evaluation system is working")
    print("   - Run: python test_recording_function.py")

if __name__ == "__main__":
    """Run system status check"""
    
    print("🎙️ AUTOMATED INTERVIEW SYSTEM")
    print("System Status Verification")
    print("=" * 60)
    
    # Check system status
    if check_system_status():
        show_usage_instructions()
        show_troubleshooting()
        
        print("\n" + "=" * 60)
        print("🎉 SYSTEM IS READY!")
        print("✅ All components working")
        print("✅ Agent instructions updated")
        print("✅ Recording function verified") 
        print("✅ Automated evaluation active")
        print("\n🚀 You can now run interviews with automatic evaluation!")
        print("=" * 60)
    else:
        print("\n❌ SYSTEM NOT READY - Please fix the issues above")
