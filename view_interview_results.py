"""
Interview Results Viewer
View complete responses and evaluations for any interview session
"""

import sqlite3
import json
from datetime import datetime

def view_interview_results(session_id=None):
    """View complete interview results"""
    
    print("🎯 Interview Results Viewer")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('interview_sessions.db')
        cursor = conn.cursor()
        
        # If no session_id provided, show all available sessions
        if not session_id:
            print("\n📋 Available Interview Sessions:")
            print("-" * 40)
            cursor.execute("""
                SELECT cp.session_id, cp.name, cp.position, 
                       COALESCE(iss.status, 'in_progress') as status,
                       COALESCE(iss.total_responses, 0) as responses
                FROM candidate_profiles cp
                LEFT JOIN interview_sessions iss ON cp.session_id = iss.session_id
                ORDER BY cp.created_at DESC
            """)
            sessions = cursor.fetchall()
            
            if not sessions:
                print("❌ No interview sessions found")
                return
            
            for i, (sid, name, position, status, responses) in enumerate(sessions, 1):
                print(f"   {i}. Session: {sid}")
                print(f"      Candidate: {name}")
                print(f"      Position: {position}")
                print(f"      Status: {status}")
                print(f"      Responses: {responses}")
                print()
            
            # Let user choose a session
            try:
                choice = input("Enter session number to view details (or session_id): ").strip()
                if choice.isdigit():
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(sessions):
                        session_id = sessions[choice_idx][0]
                    else:
                        print("❌ Invalid session number")
                        return
                else:
                    session_id = choice
            except (ValueError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                return
        
        # Show detailed results for the selected session
        print(f"\n🎯 Detailed Results for Session: {session_id}")
        print("=" * 60)
        
        # Get candidate profile
        cursor.execute("SELECT * FROM candidate_profiles WHERE session_id = ?", (session_id,))
        profile = cursor.fetchone()
        
        if not profile:
            print(f"❌ Session {session_id} not found")
            return
        
        print("\n👤 CANDIDATE PROFILE:")
        print("-" * 30)
        print(f"   Name: {profile[1]}")
        print(f"   Position: {profile[2]}")
        print(f"   Experience Level: {profile[3]}")
        print(f"   Skills: {profile[4]}")
        print(f"   Interview Type: {profile[5]}")
        print(f"   Created: {profile[6]}")
        
        # Get all responses and evaluations
        cursor.execute("""
            SELECT question, response, evaluation, timestamp 
            FROM interview_responses 
            WHERE session_id = ? 
            ORDER BY timestamp
        """, (session_id,))
        responses = cursor.fetchall()
        
        if not responses:
            print("\n❌ No responses found for this session")
            return
        
        print(f"\n💬 INTERVIEW RESPONSES ({len(responses)} total):")
        print("=" * 60)
        
        for i, (question, response, evaluation, timestamp) in enumerate(responses, 1):
            print(f"\n📝 QUESTION {i}:")
            print("-" * 40)
            print(f"Asked: {timestamp}")
            print(f"Q: {question}")
            
            print(f"\n💭 CANDIDATE RESPONSE:")
            print(f"A: {response}")
            
            print(f"\n⭐ AI EVALUATION:")
            try:
                # Try to parse evaluation as JSON for better formatting
                eval_data = json.loads(evaluation)
                print(f"Feedback: {eval_data.get('feedback', 'N/A')}")
                
                scores = eval_data.get('scores', {})
                if scores:
                    print("Scores:")
                    for criteria, score in scores.items():
                        print(f"   • {criteria}: {score}/10")
                
                follow_up = eval_data.get('follow_up_question', '')
                if follow_up:
                    print(f"Follow-up: {follow_up}")
                    
            except json.JSONDecodeError:
                # If not JSON, display as plain text
                print(f"Evaluation: {evaluation}")
            
            print("-" * 60)
        
        # Get overall session assessment
        cursor.execute("""
            SELECT overall_assessment, status, completed_at, total_responses 
            FROM interview_sessions 
            WHERE session_id = ?
        """, (session_id,))
        session_data = cursor.fetchone()
        
        if session_data:
            print(f"\n🏁 FINAL ASSESSMENT:")
            print("-" * 30)
            print(f"Status: {session_data[1]}")
            print(f"Completed: {session_data[2]}")
            print(f"Total Responses: {session_data[3]}")
            print(f"\nOverall Assessment:")
            print(session_data[0])
        
        conn.close()
        
        # Ask if user wants to generate a professional report
        print(f"\n📄 Generate Professional Report? (y/n): ", end="")
        try:
            if input().lower().startswith('y'):
                generate_quick_report(session_id)
        except KeyboardInterrupt:
            pass
        
        print(f"\n✅ Interview results displayed for session: {session_id}")
        
    except Exception as e:
        print(f"❌ Error viewing interview results: {e}")

def generate_quick_report(session_id):
    """Generate a quick professional report"""
    print(f"\n📄 PROFESSIONAL REPORT - Session: {session_id}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('interview_sessions.db')
        cursor = conn.cursor()
        
        # Get summary data
        cursor.execute("""
            SELECT cp.name, cp.position, cp.experience_level,
                   iss.overall_assessment, iss.total_responses
            FROM candidate_profiles cp
            LEFT JOIN interview_sessions iss ON cp.session_id = iss.session_id
            WHERE cp.session_id = ?
        """, (session_id,))
        
        data = cursor.fetchone()
        if not data:
            print("❌ No data found for report")
            return
        
        name, position, exp_level, assessment, total_responses = data
        
        # Get average scores
        cursor.execute("""
            SELECT evaluation FROM interview_responses WHERE session_id = ?
        """, (session_id,))
        evaluations = cursor.fetchall()
        
        total_scores = []
        for (eval_text,) in evaluations:
            try:
                eval_data = json.loads(eval_text)
                scores = eval_data.get('scores', {})
                for score in scores.values():
                    if isinstance(score, (int, float)):
                        total_scores.append(score)
            except:
                pass
        
        avg_score = sum(total_scores) / len(total_scores) if total_scores else 0
        
        print(f"CANDIDATE: {name}")
        print(f"POSITION: {position}")
        print(f"EXPERIENCE: {exp_level}")
        print(f"QUESTIONS ANSWERED: {total_responses or 0}")
        print(f"AVERAGE SCORE: {avg_score:.1f}/10")
        print()
        print("EXECUTIVE SUMMARY:")
        print(assessment or "No assessment available")
        print()
        
        # Simple recommendation based on score
        if avg_score >= 8:
            recommendation = "STRONG HIRE - Excellent performance across all areas"
        elif avg_score >= 6:
            recommendation = "HIRE - Good candidate with solid skills"
        elif avg_score >= 4:
            recommendation = "FURTHER INTERVIEW - Mixed results, needs additional evaluation"
        else:
            recommendation = "NO HIRE - Performance below expectations"
        
        print(f"RECOMMENDATION: {recommendation}")
        print(f"CONFIDENCE: {min(int(avg_score), 10)}/10")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")

if __name__ == "__main__":
    print("🎯 Welcome to Interview Results Viewer!")
    print("You can view complete responses and evaluations for any interview.")
    print()
    
    # Check if there are any interviews
    try:
        conn = sqlite3.connect('interview_sessions.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM candidate_profiles")
        total_interviews = cursor.fetchone()[0]
        conn.close()
        
        if total_interviews == 0:
            print("❌ No interviews found. Run an interview first!")
            print("   Try: python test_complete_flow.py")
        else:
            print(f"📊 Found {total_interviews} interview session(s)")
            view_interview_results()
            
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        print("   Make sure you've run an interview first!")
