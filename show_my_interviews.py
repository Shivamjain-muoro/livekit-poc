#!/usr/bin/env python3

import sqlite3
import json
from datetime import datetime

def show_my_recent_interview():
    """Show the most recent interview sessions with all details"""
    
    conn = sqlite3.connect('interview_sessions.db')
    cursor = conn.cursor()
    
    print("🎯 YOUR RECENT INTERVIEWS")
    print("=" * 60)
    
    # Get the most recent sessions
    cursor.execute("""
        SELECT id, participant_name, participant_email, position, experience_level, 
               status, start_time, end_time, current_question_index, total_questions, created_at
        FROM sessions 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    sessions = cursor.fetchall()
    
    for i, session in enumerate(sessions, 1):
        session_id, name, email, position, exp_level, status, start_time, end_time, current_q, total_q, created_at = session
        
        print(f"\n📋 INTERVIEW {i}: {name}")
        print(f"   🆔 Session ID: {session_id}")
        print(f"   📧 Email: {email}")
        print(f"   💼 Position: {position}")
        print(f"   📊 Experience: {exp_level}")
        print(f"   🔄 Status: {status}")
        print(f"   ⏰ Created: {created_at}")
        print(f"   📈 Progress: {current_q}/{total_q} questions")
        
        if start_time:
            print(f"   🎯 Started: {start_time}")
        if end_time:
            print(f"   ✅ Ended: {end_time}")
        
        # Get all questions for this session
        cursor.execute("""
            SELECT id, question_text, question_type, is_asked, asked_at, order_index
            FROM questions 
            WHERE session_id = ? 
            ORDER BY order_index
        """, (session_id,))
        questions = cursor.fetchall()
        
        print(f"\n   📝 QUESTIONS ({len(questions)}):")
        for q_id, q_text, q_type, is_asked, asked_at, order_idx in questions:
            status_icon = "✅" if is_asked else "⏳"
            print(f"      {status_icon} Q{order_idx + 1}: {q_text}")
            if asked_at:
                print(f"           🕐 Asked at: {asked_at}")
        
        # Get all answers for this session
        cursor.execute("""
            SELECT a.id, a.question_id, a.answer_text, a.duration, a.submitted_at, q.question_text
            FROM answers a
            JOIN questions q ON a.question_id = q.id
            WHERE a.session_id = ?
            ORDER BY a.submitted_at
        """, (session_id,))
        answers = cursor.fetchall()
        
        if answers:
            print(f"\n   💬 YOUR RESPONSES ({len(answers)}):")
            for j, (answer_id, question_id, answer_text, duration, submitted_at, question_text) in enumerate(answers, 1):
                print(f"\n      🗣️ RESPONSE {j}:")
                print(f"         ❓ Question: {question_text}")
                print(f"         💭 Your Answer: {answer_text}")
                print(f"         ⏱️ Duration: {duration} seconds")
                print(f"         📅 Submitted: {submitted_at}")
                
                # Get feedback for this answer
                cursor.execute("""
                    SELECT score, feedback_text, criteria_scores, strengths, improvements, evaluated_at
                    FROM feedback 
                    WHERE answer_id = ?
                """, (answer_id,))
                feedback_row = cursor.fetchone()
                
                if feedback_row:
                    score, feedback_text, criteria_scores, strengths, improvements, evaluated_at = feedback_row
                    print(f"         ⭐ EVALUATION:")
                    print(f"            📊 Overall Score: {score}/10")
                    print(f"            📝 Feedback: {feedback_text}")
                    
                    try:
                        if criteria_scores and criteria_scores != '{}':
                            scores = json.loads(criteria_scores)
                            print(f"            🎯 Detailed Scores: {scores}")
                    except:
                        pass
                    
                    try:
                        if strengths and strengths != '[]':
                            strengths_list = json.loads(strengths)
                            print(f"            💪 Strengths: {', '.join(strengths_list)}")
                    except:
                        pass
                    
                    try:
                        if improvements and improvements != '[]':
                            improvements_list = json.loads(improvements)
                            print(f"            📈 Areas to Improve: {', '.join(improvements_list)}")
                    except:
                        pass
                    
                    print(f"            🕐 Evaluated at: {evaluated_at}")
        
        print("\n" + "-" * 60)
    
    conn.close()

if __name__ == "__main__":
    show_my_recent_interview()
