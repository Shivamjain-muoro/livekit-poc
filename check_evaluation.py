"""
Interview Evaluation Checker
Check your completed interview evaluation results
"""

import sqlite3
import json
from datetime import datetime
import os

def get_db_path():
    """Get the database path"""
    # Check multiple possible locations
    possible_paths = [
        "interview_sessions.db",
        "database/interview_sessions.db",
        os.path.join(os.getcwd(), "interview_sessions.db")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return "interview_sessions.db"  # Default

def check_recent_interviews():
    """Check recent interview sessions"""
    
    db_path = get_db_path()
    print(f"🗄️ CHECKING DATABASE: {db_path}")
    print("=" * 60)
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        print(f"Looking for: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📊 Database tables: {[table[0] for table in tables]}")
        
        # Get recent sessions
        cursor.execute("""
            SELECT session_id, candidate_name, position, start_time, end_time, status
            FROM interview_sessions 
            ORDER BY start_time DESC 
            LIMIT 10
        """)
        sessions = cursor.fetchall()
        
        if not sessions:
            print("❌ No interview sessions found!")
            print("💡 Make sure you completed an interview and the agent recorded it.")
            return
        
        print(f"\\n📋 RECENT INTERVIEW SESSIONS ({len(sessions)} found):")
        print("-" * 60)
        
        for i, session in enumerate(sessions, 1):
            session_id, candidate_name, position, start_time, end_time, status = session
            print(f"{i}. Session ID: {session_id}")
            print(f"   👤 Candidate: {candidate_name}")
            print(f"   💼 Position: {position}")
            print(f"   ⏰ Start: {start_time}")
            print(f"   🏁 End: {end_time}")
            print(f"   📊 Status: {status}")
            print()
        
        # Get the most recent session for detailed check
        latest_session_id = sessions[0][0]
        print(f"🔍 CHECKING LATEST SESSION: {latest_session_id}")
        print("=" * 60)
        
        # Check Q&A data
        cursor.execute("""
            SELECT question, response, evaluation_score, technical_score, communication_score
            FROM candidate_responses 
            WHERE session_id = ?
            ORDER BY timestamp DESC
        """, (latest_session_id,))
        responses = cursor.fetchall()
        
        if responses:
            print(f"✅ Found {len(responses)} Q&A exchanges:")
            for i, (question, response, eval_score, tech_score, comm_score) in enumerate(responses[:5], 1):
                print(f"\\n{i}. Q: {question[:60]}...")
                print(f"   A: {response[:60]}...")
                print(f"   📊 Scores - Eval: {eval_score}, Tech: {tech_score}, Comm: {comm_score}")
        else:
            print("❌ No Q&A responses found for this session!")
        
        # Check evaluation data
        cursor.execute("""
            SELECT overall_score, technical_score, communication_score, 
                   problem_solving_score, recommendation, strengths, areas_of_concern
            FROM automated_evaluations 
            WHERE session_id = ?
        """, (latest_session_id,))
        evaluation = cursor.fetchone()
        
        if evaluation:
            overall, technical, communication, problem_solving, recommendation, strengths, concerns = evaluation
            print(f"\\n🎯 AUTOMATED EVALUATION RESULTS:")
            print("-" * 40)
            print(f"📊 Overall Score: {overall}/100")
            print(f"🔧 Technical Score: {technical}/100")
            print(f"💬 Communication Score: {communication}/100")
            print(f"🧩 Problem Solving Score: {problem_solving}/100")
            print(f"\\n💡 Recommendation: {recommendation}")
            print(f"\\n✅ Strengths: {strengths}")
            print(f"\\n⚠️ Areas of Concern: {concerns}")
        else:
            print("❌ No automated evaluation found!")
            print("💡 The background evaluation might still be processing.")
        
        conn.close()
        
        return latest_session_id
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return None

def generate_detailed_report(session_id):
    """Generate detailed report for a session"""
    
    print(f"\\n📄 GENERATING DETAILED REPORT FOR: {session_id}")
    print("=" * 60)
    
    try:
        from report_generator import generate_session_report
        
        # Get Google API key
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            print("❌ GOOGLE_API_KEY not found in environment")
            return
        
        print("🤖 Generating comprehensive AI report...")
        report = generate_session_report(session_id, google_api_key)
        
        if isinstance(report, dict) and "error" not in report:
            print("✅ Report generated successfully!")
            print("\\n📊 EXECUTIVE SUMMARY:")
            print("-" * 40)
            if "report_formats" in report and "executive_summary" in report["report_formats"]:
                print(report["report_formats"]["executive_summary"])
            
            print("\\n🎯 OVERALL ASSESSMENT:")
            print("-" * 40)
            if "overall_assessment" in report:
                assessment = report["overall_assessment"]
                for key, value in assessment.items():
                    print(f"{key.replace('_', ' ').title()}: {value}")
        else:
            print(f"❌ Error generating report: {report}")
            
    except Exception as e:
        print(f"❌ Error generating detailed report: {e}")

def main():
    print("🔍 INTERVIEW EVALUATION CHECKER")
    print("=" * 60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('config/.env')
    load_dotenv()
    
    # Check recent interviews
    latest_session_id = check_recent_interviews()
    
    if latest_session_id:
        print("\\n" + "=" * 60)
        choice = input("\\n📄 Generate detailed AI report? (y/n): ").lower().strip()
        
        if choice == 'y':
            generate_detailed_report(latest_session_id)
    
    print("\\n✅ Evaluation check complete!")

if __name__ == "__main__":
    main()
