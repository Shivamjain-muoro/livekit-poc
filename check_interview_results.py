"""
Quick Interview Results Checker
Simple tool to check automated evaluation results for any interview session
"""

import sqlite3
import os
import json
from datetime import datetime

def check_interview_results(session_id=None):
    """Check interview results for a specific session or show recent sessions"""
    
    db_path = os.path.join("database", "interview_evaluations.db")
    
    if not os.path.exists(db_path):
        print("❌ Database not found. No interviews have been conducted yet.")
        return
    
    try:
        with sqlite3.connect(db_path) as conn:
            if session_id:
                # Show specific session results
                print(f"🔍 CHECKING RESULTS FOR SESSION: {session_id}")
                print("=" * 60)
                
                # Get session info
                cursor = conn.execute("""
                    SELECT session_id, candidate_name, position, start_time, end_time,
                           overall_score, technical_score, communication_score, total_questions
                    FROM interview_sessions WHERE session_id = ?
                """, (session_id,))
                
                session_data = cursor.fetchone()
                if not session_data:
                    print(f"❌ Session '{session_id}' not found.")
                    print("💡 Use without session_id to see all available sessions.")
                    return
                
                # Display session summary
                print(f"👤 Candidate: {session_data[1]}")
                print(f"💼 Position: {session_data[2]}")
                print(f"📅 Start Time: {session_data[3]}")
                print(f"📅 End Time: {session_data[4] or 'In Progress'}")
                print(f"📊 Overall Score: {session_data[5] or 0:.1f}/10")
                print(f"🔧 Technical Score: {session_data[6] or 0:.1f}/10")
                print(f"💬 Communication Score: {session_data[7] or 0:.1f}/10")
                print(f"📝 Total Questions: {session_data[8] or 0}")
                
                # Get all Q&A exchanges with evaluations
                cursor = conn.execute("""
                    SELECT question, response, response_duration, overall_score,
                           correctness_score, completeness_score, clarity_score,
                           skill_relevance_score, fluency_score, confidence_score,
                           key_skills_demonstrated, areas_of_concern, evaluated_at
                    FROM interview_exchanges 
                    WHERE session_id = ?
                    ORDER BY timestamp
                """, (session_id,))
                
                exchanges = cursor.fetchall()
                
                if exchanges:
                    print(f"\n📋 Q&A EXCHANGES ({len(exchanges)} total):")
                    print("=" * 60)
                    
                    for i, exchange in enumerate(exchanges, 1):
                        question, response, duration, overall_score, correctness, completeness, clarity, skill_relevance, fluency, confidence, skills, concerns, evaluated = exchange
                        
                        print(f"\n🔹 Exchange {i}:")
                        print(f"   ❓ Question: {question}")
                        print(f"   💬 Response: {response}")
                        print(f"   ⏱️ Duration: {duration}s")
                        
                        if evaluated:
                            print(f"   📊 EVALUATION SCORES:")
                            print(f"      Overall: {overall_score:.1f}/10")
                            print(f"      Technical Correctness: {correctness:.1f}/10")
                            print(f"      Completeness: {completeness:.1f}/10")
                            print(f"      Communication Clarity: {clarity:.1f}/10")
                            print(f"      Skill Relevance: {skill_relevance:.1f}/10")
                            print(f"      Fluency: {fluency:.1f}/10")
                            print(f"      Confidence: {confidence:.1f}/10")
                            
                            if skills:
                                try:
                                    skills_list = json.loads(skills)
                                    if skills_list:
                                        print(f"      💪 Skills Demonstrated: {', '.join(skills_list)}")
                                except:
                                    pass
                            
                            if concerns:
                                try:
                                    concerns_list = json.loads(concerns)
                                    if concerns_list:
                                        print(f"      ⚠️ Areas of Concern: {', '.join(concerns_list)}")
                                except:
                                    pass
                        else:
                            print(f"   ⏳ Evaluation: Pending...")
                else:
                    print(f"\n📋 No Q&A exchanges found for this session.")
            
            else:
                # Show all available sessions
                print("📋 ALL INTERVIEW SESSIONS:")
                print("=" * 60)
                
                cursor = conn.execute("""
                    SELECT session_id, candidate_name, start_time, overall_score, 
                           technical_score, communication_score, total_questions
                    FROM interview_sessions 
                    ORDER BY start_time DESC
                """)
                
                sessions = cursor.fetchall()
                
                if sessions:
                    print(f"Found {len(sessions)} interview sessions:\n")
                    
                    for session in sessions:
                        session_id, name, start_time, overall, technical, comm, questions = session
                        
                        # Format start time
                        try:
                            start_dt = datetime.fromisoformat(start_time)
                            formatted_time = start_dt.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            formatted_time = start_time
                        
                        print(f"🔹 Session: {session_id}")
                        print(f"   👤 Candidate: {name}")
                        print(f"   📅 Date: {formatted_time}")
                        print(f"   📊 Overall: {overall or 0:.1f}/10 | Technical: {technical or 0:.1f}/10 | Communication: {comm or 0:.1f}/10")
                        print(f"   📝 Questions: {questions or 0}")
                        print()
                    
                    print("💡 To see detailed results for a specific session:")
                    print("   python check_interview_results.py <session_id>")
                else:
                    print("No interview sessions found.")
    
    except Exception as e:
        print(f"❌ Error checking results: {e}")
        import traceback
        traceback.print_exc()

def show_summary_stats():
    """Show summary statistics"""
    print("\n📊 INTERVIEW SYSTEM STATISTICS:")
    print("=" * 60)
    
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
            
            # Average scores
            cursor = conn.execute("SELECT AVG(overall_score) FROM interview_sessions WHERE overall_score > 0")
            avg_overall = cursor.fetchone()[0] or 0
            
            cursor = conn.execute("SELECT AVG(technical_score) FROM interview_sessions WHERE technical_score > 0")
            avg_technical = cursor.fetchone()[0] or 0
            
            cursor = conn.execute("SELECT AVG(communication_score) FROM interview_sessions WHERE communication_score > 0")
            avg_communication = cursor.fetchone()[0] or 0
            
            print(f"📈 Total Sessions: {total_sessions}")
            print(f"📈 Total Q&A Exchanges: {total_exchanges}")
            print(f"📈 Evaluated Exchanges: {evaluated_exchanges}")
            print(f"📈 Evaluation Coverage: {(evaluated_exchanges/total_exchanges*100):.1f}%" if total_exchanges > 0 else "📈 Evaluation Coverage: 0%")
            print(f"📊 Average Overall Score: {avg_overall:.1f}/10")
            print(f"🔧 Average Technical Score: {avg_technical:.1f}/10")
            print(f"💬 Average Communication Score: {avg_communication:.1f}/10")
            
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")

if __name__ == "__main__":
    """Main execution"""
    import sys
    
    print("🔍 INTERVIEW RESULTS CHECKER")
    print("Automated Evaluation System - Results Display")
    print("=" * 60)
    
    # Check if session ID provided as command line argument
    if len(sys.argv) > 1:
        session_id = sys.argv[1]
        check_interview_results(session_id)
    else:
        check_interview_results()
    
    # Show summary statistics
    show_summary_stats()
    
    print("\n💡 USAGE:")
    print("   python check_interview_results.py                    # Show all sessions")
    print("   python check_interview_results.py <session_id>       # Show specific session details")
    print("=" * 60)
