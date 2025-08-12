#!/usr/bin/env python3
"""
Comprehensive Interview Session Evaluation and Report Generator
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Any

def get_db_connection():
    """Get database connection"""
    db_path = os.path.join("database", "interview_evaluations.db")
    return sqlite3.connect(db_path)

def get_session_details(session_id: str) -> Dict[str, Any]:
    """Get comprehensive session details"""
    
    with get_db_connection() as conn:
        # Get session info
        cursor = conn.execute("""
            SELECT session_id, candidate_name, position, start_time, end_time, status,
                   overall_score, technical_score, communication_score, fluency_score, confidence_score
            FROM interview_sessions 
            WHERE session_id = ?
        """, (session_id,))
        
        session_row = cursor.fetchone()
        if not session_row:
            return {"error": f"Session {session_id} not found"}
        
        session_data = {
            "session_id": session_row[0],
            "candidate_name": session_row[1], 
            "position": session_row[2],
            "start_time": session_row[3],
            "end_time": session_row[4],
            "status": session_row[5],
            "overall_score": session_row[6],
            "technical_score": session_row[7],
            "communication_score": session_row[8],
            "fluency_score": session_row[9],
            "confidence_score": session_row[10]
        }
        
        # Calculate duration
        if session_data["start_time"] and session_data["end_time"]:
            try:
                start_dt = datetime.fromisoformat(session_data["start_time"])
                end_dt = datetime.fromisoformat(session_data["end_time"])
                duration_minutes = (end_dt - start_dt).total_seconds() / 60
                session_data["duration_minutes"] = round(duration_minutes, 1)
            except:
                session_data["duration_minutes"] = 0
        
        # Get Q&A exchanges
        cursor = conn.execute("""
            SELECT question, response, timestamp, response_duration,
                   relevance_score, clarity_score, depth_score,
                   ai_evaluation, key_points, concerns
            FROM interview_exchanges 
            WHERE session_id = ?
            ORDER BY timestamp
        """, (session_id,))
        
        exchanges = []
        for row in cursor.fetchall():
            exchange = {
                "question": row[0],
                "response": row[1], 
                "timestamp": row[2],
                "response_duration": row[3],
                "relevance_score": row[4],
                "clarity_score": row[5],
                "depth_score": row[6],
                "ai_evaluation": row[7],
                "key_points": row[8],
                "concerns": row[9]
            }
            exchanges.append(exchange)
        
        session_data["qa_exchanges"] = exchanges
        session_data["total_exchanges"] = len(exchanges)
        
        return session_data

def generate_evaluation_report(session_id: str) -> Dict[str, Any]:
    """Generate comprehensive evaluation report"""
    
    print(f"📊 GENERATING EVALUATION REPORT FOR SESSION: {session_id}")
    print("=" * 60)
    
    session_data = get_session_details(session_id)
    
    if "error" in session_data:
        return session_data
    
    # Display session overview
    print(f"🎯 SESSION OVERVIEW:")
    print(f"   👤 Candidate: {session_data['candidate_name']}")
    print(f"   💼 Position: {session_data['position']}")
    print(f"   📅 Date: {session_data['start_time'][:19] if session_data['start_time'] else 'Unknown'}")
    print(f"   ⏱️  Duration: {session_data.get('duration_minutes', 0)} minutes")
    print(f"   📊 Status: {session_data['status']}")
    print(f"   💬 Q&A Exchanges: {session_data['total_exchanges']}")
    print()
    
    # Overall scores
    print(f"🎯 OVERALL SCORES:")
    scores = {
        "Overall": session_data.get('overall_score'),
        "Technical": session_data.get('technical_score'), 
        "Communication": session_data.get('communication_score'),
        "Fluency": session_data.get('fluency_score'),
        "Confidence": session_data.get('confidence_score')
    }
    
    for score_name, score_value in scores.items():
        if score_value is not None:
            print(f"   {score_name}: {score_value}/10")
        else:
            print(f"   {score_name}: Not evaluated")
    print()
    
    # Detailed Q&A Analysis
    if session_data['qa_exchanges']:
        print(f"📝 DETAILED Q&A ANALYSIS:")
        print("=" * 40)
        
        for i, exchange in enumerate(session_data['qa_exchanges'], 1):
            print(f"\n🔍 EXCHANGE #{i}")
            print(f"❓ Question: {exchange['question']}")
            print(f"💬 Response: {exchange['response']}")
            print(f"⏱️  Response Time: {exchange['response_duration']}s")
            
            # Scores
            print(f"📊 Scores:")
            if exchange['relevance_score']:
                print(f"   Relevance: {exchange['relevance_score']}/10")
            if exchange['clarity_score']:
                print(f"   Clarity: {exchange['clarity_score']}/10") 
            if exchange['depth_score']:
                print(f"   Depth: {exchange['depth_score']}/10")
            
            # AI Evaluation
            if exchange['ai_evaluation']:
                print(f"🤖 AI Evaluation: {exchange['ai_evaluation']}")
            
            # Key Points
            if exchange['key_points']:
                print(f"🔑 Key Points: {exchange['key_points']}")
                
            # Concerns
            if exchange['concerns']:
                print(f"⚠️  Concerns: {exchange['concerns']}")
            
            print("-" * 30)
        
        # Calculate average scores
        relevance_scores = [e['relevance_score'] for e in session_data['qa_exchanges'] if e['relevance_score']]
        clarity_scores = [e['clarity_score'] for e in session_data['qa_exchanges'] if e['clarity_score']]
        depth_scores = [e['depth_score'] for e in session_data['qa_exchanges'] if e['depth_score']]
        
        print(f"\n📊 AVERAGE EXCHANGE SCORES:")
        if relevance_scores:
            print(f"   Average Relevance: {sum(relevance_scores)/len(relevance_scores):.1f}/10")
        if clarity_scores:
            print(f"   Average Clarity: {sum(clarity_scores)/len(clarity_scores):.1f}/10")
        if depth_scores:
            print(f"   Average Depth: {sum(depth_scores)/len(depth_scores):.1f}/10")
    
    else:
        print("📝 Q&A ANALYSIS:")
        print("   ⚠️  No structured Q&A exchanges found")
        print("   🔍 This suggests a natural conversation occurred")
        print("   💡 Future interviews: AI should use record_candidate_response more")
    
    print()
    return session_data

def list_available_sessions() -> List[Dict[str, Any]]:
    """List all available sessions for evaluation"""
    
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT session_id, candidate_name, position, start_time, status,
                   (SELECT COUNT(*) FROM interview_exchanges WHERE session_id = interview_sessions.session_id) as exchange_count
            FROM interview_sessions 
            ORDER BY start_time DESC
        """)
        
        sessions = []
        for row in cursor.fetchall():
            session = {
                "session_id": row[0],
                "candidate_name": row[1],
                "position": row[2], 
                "start_time": row[3],
                "status": row[4],
                "exchange_count": row[5]
            }
            sessions.append(session)
        
        return sessions

def main():
    """Main evaluation interface"""
    
    print("🎯 INTERVIEW SESSION EVALUATION SYSTEM")
    print("=" * 50)
    
    # List available sessions
    sessions = list_available_sessions()
    
    if not sessions:
        print("❌ No interview sessions found")
        return
    
    print(f"📋 AVAILABLE SESSIONS ({len(sessions)} total):")
    print()
    
    for i, session in enumerate(sessions, 1):
        print(f"{i}. 🗂️  {session['session_id'][:20]}...")
        print(f"   👤 {session['candidate_name']} - {session['position']}")
        print(f"   📅 {session['start_time'][:19] if session['start_time'] else 'Unknown'}")
        print(f"   📊 {session['status']} | 💬 {session['exchange_count']} exchanges")
        print()
    
    # Get user choice
    try:
        choice = input(f"Enter session number (1-{len(sessions)}) or session_id: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(sessions):
            selected_session = sessions[int(choice) - 1]
            session_id = selected_session['session_id']
        else:
            session_id = choice
        
        print(f"\n🔍 Analyzing session: {session_id}")
        print("=" * 50)
        
        # Generate comprehensive report
        report = generate_evaluation_report(session_id)
        
        if "error" not in report:
            print("\n✅ EVALUATION COMPLETE!")
            print(f"📄 Full session data available in database")
            print(f"🎯 Session {session_id} analysis finished")
        
    except KeyboardInterrupt:
        print("\n👋 Evaluation cancelled by user")
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")

if __name__ == "__main__":
    main()
