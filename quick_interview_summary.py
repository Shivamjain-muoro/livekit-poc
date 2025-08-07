"""
Quick Interview Summary Dashboard
Get a quick overview of all interview sessions and their key metrics
"""

import sqlite3
import os
import json
from datetime import datetime

def quick_summary():
    """Display a quick summary of all interviews"""
    print("🎯 INTERVIEW DASHBOARD - QUICK SUMMARY")
    print("=" * 60)
    
    db_path = os.path.join("database", "interview_evaluations.db")
    
    if not os.path.exists(db_path):
        print("❌ No interview database found.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Get session summary
            sessions_cursor = conn.execute("""
                SELECT session_id, candidate_name, position, start_time, 
                       overall_score, technical_score, communication_score, status
                FROM interview_sessions 
                ORDER BY start_time DESC
            """)
            
            sessions = sessions_cursor.fetchall()
            
            if not sessions:
                print("❌ No interview sessions found.")
                return
            
            print(f"📊 TOTAL INTERVIEWS CONDUCTED: {len(sessions)}")
            print("")
            
            total_score = 0
            completed_count = 0
            
            for session in sessions:
                session_id, name, position, start_time, overall_score, tech_score, comm_score, status = session
                
                print(f"🎤 Session: {session_id}")
                print(f"   👤 Candidate: {name}")
                print(f"   💼 Position: {position}")
                print(f"   📅 Date: {start_time}")
                print(f"   📊 Overall Score: {overall_score or 0:.1f}/10")
                print(f"   🔧 Technical: {tech_score or 0:.1f}/10")
                print(f"   💬 Communication: {comm_score or 0:.1f}/10")
                print(f"   📋 Status: {status}")
                
                # Get exchange count
                exchanges_cursor = conn.execute("""
                    SELECT COUNT(*) FROM interview_exchanges WHERE session_id = ?
                """, (session_id,))
                exchange_count = exchanges_cursor.fetchone()[0]
                print(f"   💭 Questions Asked: {exchange_count}")
                
                # Quick evaluation preview
                if overall_score and overall_score > 0:
                    if overall_score >= 8:
                        recommendation = "🟢 STRONG HIRE"
                    elif overall_score >= 6:
                        recommendation = "🟡 HIRE WITH RESERVATIONS"
                    else:
                        recommendation = "🔴 DO NOT HIRE"
                    
                    print(f"   🎯 Quick Recommendation: {recommendation}")
                    total_score += overall_score
                    completed_count += 1
                
                print("")
            
            # Overall statistics
            if completed_count > 0:
                avg_score = total_score / completed_count
                print("📈 SUMMARY STATISTICS:")
                print(f"   Average Score: {avg_score:.1f}/10")
                print(f"   Completed Evaluations: {completed_count}/{len(sessions)}")
                
                # Score distribution
                high_performers = sum(1 for s in sessions if (s[4] or 0) >= 8)
                medium_performers = sum(1 for s in sessions if 6 <= (s[4] or 0) < 8)
                low_performers = sum(1 for s in sessions if 0 < (s[4] or 0) < 6)
                
                print(f"   🟢 Strong Candidates: {high_performers}")
                print(f"   🟡 Medium Candidates: {medium_performers}")
                print(f"   🔴 Weak Candidates: {low_performers}")
    
    except Exception as e:
        print(f"❌ Error reading interview data: {e}")

def get_latest_interview():
    """Get details of the most recent interview"""
    print("\n🕐 LATEST INTERVIEW DETAILS")
    print("=" * 40)
    
    db_path = os.path.join("database", "interview_evaluations.db")
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Get latest session
            latest_cursor = conn.execute("""
                SELECT session_id, candidate_name, position, start_time, 
                       overall_score, technical_score, communication_score
                FROM interview_sessions 
                ORDER BY start_time DESC LIMIT 1
            """)
            
            latest = latest_cursor.fetchone()
            if not latest:
                print("❌ No interviews found.")
                return
            
            session_id, name, position, start_time, overall_score, tech_score, comm_score = latest
            
            print(f"👤 Latest Candidate: {name}")
            print(f"💼 Position: {position}")
            print(f"📅 Interview Date: {start_time}")
            print(f"📊 Final Scores:")
            print(f"   Overall: {overall_score or 0:.1f}/10")
            print(f"   Technical: {tech_score or 0:.1f}/10")
            print(f"   Communication: {comm_score or 0:.1f}/10")
            
            # Get latest exchanges
            exchanges_cursor = conn.execute("""
                SELECT question, response, relevance_score, clarity_score, depth_score,
                       ai_evaluation
                FROM interview_exchanges 
                WHERE session_id = ?
                ORDER BY timestamp DESC LIMIT 3
            """, (session_id,))
            
            exchanges = exchanges_cursor.fetchall()
            
            print(f"\n💬 Recent Q&A ({len(exchanges)} shown):")
            for i, exchange in enumerate(exchanges, 1):
                question, response, rel_score, clar_score, depth_score, evaluation = exchange
                print(f"\n   Q{i}: {question}")
                print(f"   A{i}: {response[:100]}{'...' if len(response) > 100 else ''}")
                print(f"   Scores: R:{rel_score or 0:.1f} C:{clar_score or 0:.1f} D:{depth_score or 0:.1f}")
    
    except Exception as e:
        print(f"❌ Error getting latest interview: {e}")

if __name__ == "__main__":
    quick_summary()
    get_latest_interview()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Run 'python view_interview_reports.py' for detailed analysis")
    print("2. Use option 3 in the report viewer for comprehensive reports")
    print("3. Export data using option 4 for external analysis")
    print("4. Check your database files for all stored evaluations")
