#!/usr/bin/env python3
"""
Generate Interview Report from Database
Analyzes existing interview data and creates evaluation reports
"""

import sqlite3
import json
from datetime import datetime

def generate_interview_evaluation():
    """Generate evaluation report from existing interview data"""
    
    print("📊 INTERVIEW EVALUATION GENERATOR")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('database/interview_sessions.db')
        cursor = conn.cursor()
        
        # Get the most recent session with responses
        cursor.execute('''
            SELECT s.*, 
                   (SELECT COUNT(*) FROM interview_responses WHERE session_id = s.session_id) as response_count
            FROM sessions s 
            WHERE EXISTS (SELECT 1 FROM interview_responses WHERE session_id = s.session_id)
            ORDER BY s.created_at DESC 
            LIMIT 1
        ''')
        
        session = cursor.fetchone()
        
        if not session:
            print("❌ No sessions with responses found")
            return
        
        session_id = session[6]  # session_id is at index 6
        candidate_name = session[1]
        position = session[3]
        print(f"🎯 Analyzing session: {session_id}")
        print(f"👤 Candidate: {candidate_name}")
        print(f"💼 Position: {position}")
        print()
        
        # Get all responses for this session
        cursor.execute('''
            SELECT question, answer, evaluation, timestamp 
            FROM interview_responses 
            WHERE session_id = ? 
            ORDER BY timestamp
        ''', (session_id,))
        
        responses = cursor.fetchall()
        print(f"💬 Found {len(responses)} Q&A exchanges")
        print()
        
        # Analyze each response
        total_score = 0
        detailed_analysis = []
        
        for i, (question, answer, evaluation, timestamp) in enumerate(responses, 1):
            print(f"📝 Q&A #{i}")
            print(f"❓ Question: {question}")
            print(f"💬 Answer: {answer[:100]}...")
            print(f"📊 Evaluation: {evaluation[:100]}...")
            print(f"🕐 Time: {timestamp}")
            print()
            
            # Simple scoring based on answer length and evaluation
            score = min(85, max(40, len(answer) // 10 + 50))  # Basic scoring
            total_score += score
            
            detailed_analysis.append({
                "question": question,
                "answer": answer,
                "evaluation": evaluation,
                "score": score,
                "timestamp": timestamp
            })
        
        # Calculate overall metrics
        average_score = total_score / len(responses) if responses else 0
        
        print("🎯 INTERVIEW EVALUATION SUMMARY")
        print("=" * 40)
        print(f"👤 Candidate: {candidate_name}")
        print(f"💼 Position: {position}")
        print(f"📅 Session: {session_id}")
        print(f"💬 Total Q&A: {len(responses)}")
        print(f"📊 Average Score: {average_score:.1f}/100")
        print()
        
        # Performance categorization
        if average_score >= 80:
            performance = "🟢 EXCELLENT"
            recommendation = "STRONG HIRE - Candidate demonstrated excellent knowledge and communication"
        elif average_score >= 70:
            performance = "🟡 GOOD"
            recommendation = "HIRE - Candidate shows good potential with some areas for growth"
        elif average_score >= 60:
            performance = "🟠 AVERAGE"
            recommendation = "CONSIDER - Mixed performance, may need additional evaluation"
        else:
            performance = "🔴 NEEDS IMPROVEMENT"
            recommendation = "NOT RECOMMENDED - Significant gaps in knowledge or communication"
        
        print(f"🎯 Overall Performance: {performance}")
        print(f"💡 Recommendation: {recommendation}")
        print()
        
        # Detailed breakdown
        print("📋 DETAILED Q&A ANALYSIS")
        print("=" * 30)
        for i, analysis in enumerate(detailed_analysis, 1):
            print(f"Question {i}: {analysis['score']}/100")
            print(f"  📝 {analysis['question'][:60]}...")
            print(f"  💬 Answer length: {len(analysis['answer'])} characters")
            print(f"  📊 {analysis['evaluation'][:80]}...")
            print()
        
        # Save report to file
        report_data = {
            "session_id": session_id,
            "candidate": candidate_name,
            "position": position,
            "total_qa": len(responses),
            "average_score": average_score,
            "performance": performance,
            "recommendation": recommendation,
            "detailed_analysis": detailed_analysis,
            "generated_at": datetime.now().isoformat()
        }
        
        report_file = f"interview_report_{session_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"💾 Report saved to: {report_file}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")

def show_all_available_interviews():
    """Show all interviews available for evaluation"""
    
    print("\n📋 ALL AVAILABLE INTERVIEWS")
    print("=" * 40)
    
    try:
        conn = sqlite3.connect('database/interview_sessions.db')
        cursor = conn.cursor()
        
        # Get all sessions with their response counts
        cursor.execute('''
            SELECT s.session_id, s.name, s.position, s.status, s.created_at,
                   (SELECT COUNT(*) FROM interview_responses WHERE session_id = s.session_id) as responses
            FROM sessions s 
            ORDER BY s.created_at DESC
        ''')
        
        sessions = cursor.fetchall()
        
        print(f"Found {len(sessions)} total interview sessions:")
        print()
        
        for session in sessions:
            session_id, name, position, status, created_at, response_count = session
            print(f"🆔 {session_id}")
            print(f"👤 {name} - {position}")
            print(f"📊 Status: {status}")
            print(f"💬 Responses: {response_count}")
            print(f"📅 Created: {created_at}")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error listing interviews: {e}")

if __name__ == "__main__":
    show_all_available_interviews()
    generate_interview_evaluation()
