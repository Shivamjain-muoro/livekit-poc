"""
Interview Evaluation and Feedback Viewer
Access comprehensive reports and evaluations from completed interviews
"""

import sqlite3
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from report_generator import generate_session_report, get_executive_summary, get_hiring_recommendation

# Load environment
load_dotenv()

class InterviewReportViewer:
    """
    View and analyze completed interview reports and evaluations
    """
    
    def __init__(self):
        self.db_path = os.path.join("database", "interview_evaluations.db")
        self.old_db_path = os.path.join("database", "interview_sessions.db")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
    def list_all_sessions(self):
        """List all available interview sessions"""
        print("📋 AVAILABLE INTERVIEW SESSIONS")
        print("=" * 50)
        
        sessions = []
        
        # Check new database
        if os.path.exists(self.db_path):
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("""
                        SELECT session_id, candidate_name, position, start_time, 
                               overall_score, status
                        FROM interview_sessions 
                        ORDER BY start_time DESC
                    """)
                    
                    for row in cursor.fetchall():
                        session_id, name, position, start_time, score, status = row
                        sessions.append({
                            "session_id": session_id,
                            "candidate_name": name,
                            "position": position,
                            "start_time": start_time,
                            "overall_score": score or 0,
                            "status": status,
                            "database": "new"
                        })
                        
            except Exception as e:
                print(f"⚠️ Error reading new database: {e}")
        
        # Check old database
        if os.path.exists(self.old_db_path):
            try:
                with sqlite3.connect(self.old_db_path) as conn:
                    cursor = conn.execute("""
                        SELECT session_id, candidate_name, position, start_time, status
                        FROM interview_sessions 
                        ORDER BY start_time DESC
                    """)
                    
                    for row in cursor.fetchall():
                        session_id, name, position, start_time, status = row
                        sessions.append({
                            "session_id": session_id,
                            "candidate_name": name,
                            "position": position,
                            "start_time": start_time,
                            "overall_score": 0,
                            "status": status,
                            "database": "old"
                        })
                        
            except Exception as e:
                print(f"⚠️ Error reading old database: {e}")
        
        if not sessions:
            print("❌ No interview sessions found.")
            print("💡 Make sure you've conducted interviews and the agent has processed them.")
            return []
        
        # Display sessions
        for i, session in enumerate(sessions, 1):
            print(f"\n{i}. Session ID: {session['session_id']}")
            print(f"   👤 Candidate: {session['candidate_name']}")
            print(f"   💼 Position: {session['position']}")
            print(f"   📅 Date: {session['start_time']}")
            print(f"   📊 Score: {session['overall_score']:.1f}/10")
            print(f"   📋 Status: {session['status']}")
            print(f"   🗄️ Database: {session['database']}")
        
        return sessions
    
    def get_session_details(self, session_id):
        """Get detailed information about a specific session"""
        print(f"\n📊 DETAILED SESSION ANALYSIS: {session_id}")
        print("=" * 60)
        
        # Try new database first
        session_data = self._get_session_from_new_db(session_id)
        if not session_data:
            session_data = self._get_session_from_old_db(session_id)
        
        if not session_data:
            print(f"❌ Session {session_id} not found in any database.")
            return None
        
        return session_data
    
    def _get_session_from_new_db(self, session_id):
        """Get session data from new evaluation database"""
        if not os.path.exists(self.db_path):
            return None
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get session info
                session_cursor = conn.execute("""
                    SELECT * FROM interview_sessions WHERE session_id = ?
                """, (session_id,))
                session_row = session_cursor.fetchone()
                
                if not session_row:
                    return None
                
                # Get exchanges
                exchanges_cursor = conn.execute("""
                    SELECT question, response, timestamp, response_duration, 
                           relevance_score, clarity_score, depth_score, 
                           ai_evaluation, key_points, concerns
                    FROM interview_exchanges 
                    WHERE session_id = ? 
                    ORDER BY timestamp
                """, (session_id,))
                
                exchanges = []
                for row in exchanges_cursor.fetchall():
                    exchanges.append({
                        "question": row[0],
                        "response": row[1],
                        "timestamp": row[2],
                        "duration": row[3],
                        "relevance_score": row[4] or 0,
                        "clarity_score": row[5] or 0,
                        "depth_score": row[6] or 0,
                        "evaluation": row[7] or "",
                        "key_points": json.loads(row[8]) if row[8] else [],
                        "concerns": json.loads(row[9]) if row[9] else []
                    })
                
                return {
                    "session_id": session_row[0],
                    "candidate_name": session_row[1],
                    "position": session_row[2],
                    "start_time": session_row[3],
                    "end_time": session_row[4],
                    "overall_score": session_row[6] or 0,
                    "technical_score": session_row[7] or 0,
                    "communication_score": session_row[8] or 0,
                    "exchanges": exchanges,
                    "database": "new"
                }
                
        except Exception as e:
            print(f"⚠️ Error reading from new database: {e}")
            return None
    
    def _get_session_from_old_db(self, session_id):
        """Get session data from old database"""
        if not os.path.exists(self.old_db_path):
            return None
            
        try:
            with sqlite3.connect(self.old_db_path) as conn:
                # Get session info
                session_cursor = conn.execute("""
                    SELECT * FROM interview_sessions WHERE session_id = ?
                """, (session_id,))
                session_row = session_cursor.fetchone()
                
                if not session_row:
                    return None
                
                # Get exchanges (different schema)
                exchanges_cursor = conn.execute("""
                    SELECT question, response, timestamp, evaluation
                    FROM interview_exchanges 
                    WHERE session_id = ? 
                    ORDER BY timestamp
                """, (session_id,))
                
                exchanges = []
                for row in exchanges_cursor.fetchall():
                    exchanges.append({
                        "question": row[0],
                        "response": row[1],
                        "timestamp": row[2],
                        "evaluation": row[3] or "",
                        "relevance_score": 0,
                        "clarity_score": 0,
                        "depth_score": 0,
                        "key_points": [],
                        "concerns": []
                    })
                
                return {
                    "session_id": session_row[0],
                    "candidate_name": session_row[1],
                    "position": session_row[2],
                    "start_time": session_row[3],
                    "end_time": session_row[4] if len(session_row) > 4 else None,
                    "overall_score": 0,
                    "technical_score": 0,
                    "communication_score": 0,
                    "exchanges": exchanges,
                    "database": "old"
                }
                
        except Exception as e:
            print(f"⚠️ Error reading from old database: {e}")
            return None
    
    def display_session_summary(self, session_data):
        """Display a comprehensive summary of the session"""
        print(f"\n👤 CANDIDATE: {session_data['candidate_name']}")
        print(f"💼 POSITION: {session_data['position']}")
        print(f"📅 START TIME: {session_data['start_time']}")
        print(f"⏰ END TIME: {session_data.get('end_time', 'Not recorded')}")
        
        if session_data['database'] == 'new':
            print(f"\n📊 SCORES:")
            print(f"   Overall Score: {session_data['overall_score']:.1f}/10")
            print(f"   Technical Score: {session_data['technical_score']:.1f}/10")
            print(f"   Communication Score: {session_data['communication_score']:.1f}/10")
        
        print(f"\n💬 INTERVIEW EXCHANGES: {len(session_data['exchanges'])}")
        
        for i, exchange in enumerate(session_data['exchanges'], 1):
            print(f"\n--- Exchange {i} ---")
            print(f"❓ Question: {exchange['question']}")
            print(f"💭 Response: {exchange['response'][:200]}{'...' if len(exchange['response']) > 200 else ''}")
            
            if session_data['database'] == 'new':
                print(f"📊 Scores: Relevance: {exchange['relevance_score']:.1f}, Clarity: {exchange['clarity_score']:.1f}, Depth: {exchange['depth_score']:.1f}")
                if exchange['key_points']:
                    print(f"🔑 Key Points: {', '.join(exchange['key_points'])}")
                if exchange['concerns']:
                    print(f"⚠️ Concerns: {', '.join(exchange['concerns'])}")
            
            if exchange['evaluation']:
                print(f"📝 Evaluation: {exchange['evaluation']}")
    
    def generate_comprehensive_report(self, session_id):
        """Generate and display comprehensive report"""
        print(f"\n📊 GENERATING COMPREHENSIVE REPORT FOR: {session_id}")
        print("=" * 60)
        
        try:
            # Use the report generator
            report = generate_session_report(session_id, self.google_api_key)
            
            if "error" in report:
                print(f"⚠️ Report generation issue: {report['error']}")
                print("💡 This might mean the session data is still being processed.")
                return False
            
            # Display executive summary
            print("\n📋 EXECUTIVE SUMMARY:")
            print("-" * 30)
            executive_summary = get_executive_summary(session_id, self.google_api_key)
            print(executive_summary)
            
            # Display hiring recommendation
            print("\n🎯 HIRING RECOMMENDATION:")
            print("-" * 30)
            hiring_rec = get_hiring_recommendation(session_id, self.google_api_key)
            print(hiring_rec)
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating comprehensive report: {e}")
            return False
    
    def export_session_data(self, session_id, format="json"):
        """Export session data to file"""
        session_data = self.get_session_details(session_id)
        if not session_data:
            print(f"❌ Cannot export: Session {session_id} not found")
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interview_report_{session_id}_{timestamp}.{format}"
        
        try:
            if format == "json":
                with open(filename, 'w') as f:
                    json.dump(session_data, f, indent=2, default=str)
            else:
                # Create text report
                with open(filename, 'w') as f:
                    f.write(f"INTERVIEW REPORT\n")
                    f.write(f"================\n\n")
                    f.write(f"Candidate: {session_data['candidate_name']}\n")
                    f.write(f"Position: {session_data['position']}\n")
                    f.write(f"Date: {session_data['start_time']}\n\n")
                    
                    for i, exchange in enumerate(session_data['exchanges'], 1):
                        f.write(f"Exchange {i}:\n")
                        f.write(f"Q: {exchange['question']}\n")
                        f.write(f"A: {exchange['response']}\n")
                        if exchange['evaluation']:
                            f.write(f"Evaluation: {exchange['evaluation']}\n")
                        f.write("\n")
            
            print(f"✅ Report exported to: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Export error: {e}")
            return False

def interactive_report_viewer():
    """Interactive menu for viewing reports"""
    viewer = InterviewReportViewer()
    
    while True:
        print("\n🎯 INTERVIEW EVALUATION & FEEDBACK VIEWER")
        print("=" * 50)
        print("1. List all interview sessions")
        print("2. View detailed session analysis")
        print("3. Generate comprehensive report")
        print("4. Export session data")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            sessions = viewer.list_all_sessions()
            
        elif choice == "2":
            session_id = input("Enter session ID: ").strip()
            session_data = viewer.get_session_details(session_id)
            if session_data:
                viewer.display_session_summary(session_data)
                
        elif choice == "3":
            session_id = input("Enter session ID for comprehensive report: ").strip()
            viewer.generate_comprehensive_report(session_id)
            
        elif choice == "4":
            session_id = input("Enter session ID to export: ").strip()
            format_choice = input("Export format (json/txt): ").strip().lower()
            if format_choice not in ["json", "txt"]:
                format_choice = "json"
            viewer.export_session_data(session_id, format_choice)
            
        elif choice == "5":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    print("🎙️ INTERVIEW EVALUATION & FEEDBACK SYSTEM")
    print("Access comprehensive reports from your interview sessions")
    print("")
    
    # Check if databases exist
    if not os.path.exists("database"):
        print("❌ No database directory found. Please conduct interviews first.")
    else:
        interactive_report_viewer()
