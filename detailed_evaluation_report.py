#!/usr/bin/env python3
"""
Interview Evaluation Report Generator
Shows detailed analysis of completed interviews
"""

import sqlite3
from datetime import datetime

def generate_evaluation_report():
    print("📊 INTERVIEW EVALUATION REPORT")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('database/interview_sessions.db')
        cursor = conn.cursor()
        
        # Get all interview responses (using correct column names)
        cursor.execute("""
            SELECT session_id, question, response, evaluation, timestamp 
            FROM interview_responses 
            ORDER BY timestamp DESC
        """)
        
        all_responses = cursor.fetchall()
        print(f"💬 Total interview responses found: {len(all_responses)}")
        
        if not all_responses:
            print("❌ No interview responses found")
            return
        
        # Group by session_id
        sessions = {}
        for session_id, question, response, evaluation, timestamp in all_responses:
            if session_id not in sessions:
                sessions[session_id] = []
            sessions[session_id].append({
                'question': question,
                'response': response,
                'evaluation': evaluation,
                'timestamp': timestamp
            })
        
        print(f"🆔 Found {len(sessions)} interview sessions with responses")
        print()
        
        # Analyze each session
        for session_id, responses in sessions.items():
            print(f"🎯 SESSION ANALYSIS: {session_id}")
            print("=" * 60)
            print(f"💬 Total Q&A exchanges: {len(responses)}")
            print(f"📅 Interview period: {responses[-1]['timestamp']} to {responses[0]['timestamp']}")
            print()
            
            # Detailed Q&A analysis
            total_score = 0
            question_scores = []
            
            for i, qa in enumerate(responses, 1):
                print(f"📝 QUESTION {i}")
                print("-" * 20)
                print(f"❓ Q: {qa['question']}")
                print()
                print(f"💬 A: {qa['response']}")
                print()
                print(f"📊 EVALUATION: {qa['evaluation']}")
                print()
                
                # Calculate score based on response quality
                response_length = len(qa['response'])
                evaluation_text = qa['evaluation'].lower()
                
                # Basic scoring algorithm
                score = 50  # Base score
                
                # Response length scoring
                if response_length > 200:
                    score += 20
                elif response_length > 100:
                    score += 10
                elif response_length < 30:
                    score -= 15
                
                # Evaluation content scoring
                positive_indicators = ['good', 'excellent', 'demonstrates', 'understanding', 'clear', 'experience', 'practical', 'showcases']
                negative_indicators = ["doesn't", 'no experience', 'no idea', 'lacks', 'insufficient']
                
                for indicator in positive_indicators:
                    if indicator in evaluation_text:
                        score += 5
                
                for indicator in negative_indicators:
                    if indicator in evaluation_text:
                        score -= 15
                
                # Ensure score is within bounds
                score = max(0, min(100, score))
                
                total_score += score
                question_scores.append(score)
                
                # Score interpretation
                if score >= 80:
                    performance = "🟢 EXCELLENT"
                elif score >= 70:
                    performance = "🟡 GOOD"
                elif score >= 60:
                    performance = "🟠 AVERAGE"
                else:
                    performance = "🔴 NEEDS IMPROVEMENT"
                
                print(f"🎯 SCORE: {score}/100 {performance}")
                print(f"🕐 TIME: {qa['timestamp']}")
                print("-" * 60)
                print()
            
            # Overall session analysis
            average_score = total_score / len(responses)
            
            print(f"📈 SESSION SUMMARY")
            print("=" * 30)
            print(f"🆔 Session ID: {session_id}")
            print(f"💬 Questions answered: {len(responses)}")
            print(f"📊 Average score: {average_score:.1f}/100")
            print(f"📊 Individual scores: {question_scores}")
            print()
            
            # Overall performance assessment
            if average_score >= 80:
                overall = "🟢 EXCELLENT PERFORMANCE"
                recommendation = "✅ STRONG HIRE - Candidate demonstrated excellent knowledge and communication skills"
            elif average_score >= 70:
                overall = "🟡 GOOD PERFORMANCE"
                recommendation = "✅ HIRE - Candidate shows good potential with solid technical knowledge"
            elif average_score >= 60:
                overall = "🟠 AVERAGE PERFORMANCE"
                recommendation = "⚠️ CONSIDER - Mixed performance, may benefit from additional evaluation"
            else:
                overall = "🔴 BELOW AVERAGE"
                recommendation = "❌ NOT RECOMMENDED - Significant gaps in knowledge or communication"
            
            print(f"🎯 OVERALL ASSESSMENT: {overall}")
            print(f"💡 RECOMMENDATION: {recommendation}")
            print()
            
            # Strengths and areas for improvement
            print(f"📋 DETAILED ANALYSIS")
            print("-" * 25)
            
            strengths = []
            improvements = []
            
            for i, (score, qa) in enumerate(zip(question_scores, responses), 1):
                if score >= 75:
                    strengths.append(f"Question {i}: Strong response ({score}/100)")
                elif score < 50:
                    improvements.append(f"Question {i}: Needs improvement ({score}/100)")
            
            if strengths:
                print("✅ STRENGTHS:")
                for strength in strengths:
                    print(f"  • {strength}")
                print()
            
            if improvements:
                print("⚠️ AREAS FOR IMPROVEMENT:")
                for improvement in improvements:
                    print(f"  • {improvement}")
                print()
            
            print("=" * 80)
            print()
        
        # Generate summary across all sessions
        if len(sessions) > 1:
            print(f"🌟 MULTI-SESSION SUMMARY")
            print("=" * 30)
            all_scores = []
            total_questions = 0
            
            for session_id, responses in sessions.items():
                session_score = 0
                for qa in responses:
                    # Recalculate scores (simplified for summary)
                    score = 50
                    if len(qa['response']) > 100:
                        score += 15
                    if 'good' in qa['evaluation'].lower() or 'excellent' in qa['evaluation'].lower():
                        score += 20
                    if "doesn't" in qa['evaluation'].lower():
                        score -= 20
                    score = max(0, min(100, score))
                    session_score += score
                
                avg_session_score = session_score / len(responses)
                all_scores.append(avg_session_score)
                total_questions += len(responses)
                
                print(f"📋 {session_id}: {avg_session_score:.1f}/100 ({len(responses)} questions)")
            
            overall_average = sum(all_scores) / len(all_scores)
            print(f"\n🎯 OVERALL AVERAGE: {overall_average:.1f}/100")
            print(f"💬 Total questions across all sessions: {total_questions}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_evaluation_report()
