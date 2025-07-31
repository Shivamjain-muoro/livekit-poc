#!/usr/bin/env python3

import sqlite3
import json
from datetime import datetime

def view_recent_interviews():
    """View all recent interview data from both old and new table structures"""
    
    conn = sqlite3.connect('interview_sessions.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("RECENT INTERVIEW SESSIONS")
    print("=" * 80)
    
    # Check recent sessions from the main sessions table
    cursor.execute("""
        SELECT id, participant_name, participant_email, position, experience_level, 
               status, start_time, end_time, current_question_index, total_questions, created_at
        FROM sessions 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    recent_sessions = cursor.fetchall()
    
    if recent_sessions:
        for i, session in enumerate(recent_sessions, 1):
            session_id, name, email, position, exp_level, status, start_time, end_time, current_q, total_q, created_at = session
            
            print(f"\n📋 SESSION {i}: {session_id}")
            print(f"   👤 Candidate: {name} ({email})")
            print(f"   💼 Position: {position}")
            print(f"   📊 Experience: {exp_level}")
            print(f"   🔄 Status: {status}")
            print(f"   ⏰ Created: {created_at}")
            print(f"   📈 Progress: {current_q}/{total_q} questions")
            if start_time:
                print(f"   🎯 Started: {start_time}")
            if end_time:
                print(f"   ✅ Ended: {end_time}")
            
            # Get questions for this session
            cursor.execute("""
                SELECT question_text, question_type, is_asked, asked_at
                FROM questions 
                WHERE session_id = ? 
                ORDER BY order_index
            """, (session_id,))
            questions = cursor.fetchall()
            
            print(f"   📝 Questions ({len(questions)}):")
            for j, (q_text, q_type, is_asked, asked_at) in enumerate(questions, 1):
                status_icon = "✅" if is_asked else "⏳"
                print(f"      {status_icon} Q{j}: {q_text[:80]}...")
                if asked_at:
                    print(f"           Asked at: {asked_at}")
            
            # Get answers for this session
            cursor.execute("""
                SELECT q.question_text, a.answer_text, a.duration, a.submitted_at
                FROM answers a
                JOIN questions q ON a.question_id = q.id
                WHERE a.session_id = ?
                ORDER BY a.submitted_at
            """, (session_id,))
            answers = cursor.fetchall()
            
            if answers:
                print(f"   💬 Responses ({len(answers)}):")
                for j, (question, answer, duration, submitted_at) in enumerate(answers, 1):
                    print(f"      🗣️ Response {j} ({duration}s):")
                    print(f"         Q: {question[:60]}...")
                    print(f"         A: {answer[:100]}...")
                    print(f"         ⏰ Submitted: {submitted_at}")
            
            # Get feedback for this session
            cursor.execute("""
                SELECT f.feedback_text, f.score, f.created_at, q.question_text
                FROM feedback f
                JOIN answers a ON f.answer_id = a.id
                JOIN questions q ON a.question_id = q.id
                WHERE a.session_id = ?
                ORDER BY f.created_at
            """, (session_id,))
            feedback = cursor.fetchall()
            
            if feedback:
                print(f"   🎯 Evaluations ({len(feedback)}):")
                for j, (fb_text, score, fb_created, question) in enumerate(feedback, 1):
                    print(f"      ⭐ Evaluation {j} (Score: {score}):")
                    print(f"         Q: {question[:50]}...")
                    print(f"         📝 {fb_text[:80]}...")
                    print(f"         ⏰ Created: {fb_created}")
            
            print("-" * 60)
    
    # Also show new table structure data
    print("\n" + "=" * 80)
    print("NEW TABLE STRUCTURE DATA")
    print("=" * 80)
    
    cursor.execute("SELECT * FROM candidate_profiles ORDER BY created_at DESC")
    profiles = cursor.fetchall()
    
    cursor.execute("SELECT * FROM interview_responses ORDER BY timestamp DESC")
    responses = cursor.fetchall()
    
    cursor.execute("SELECT * FROM interview_sessions ORDER BY completed_at DESC")
    sessions = cursor.fetchall()
    
    if profiles or responses or sessions:
        print(f"\n📊 New Format Summary:")
        print(f"   Profiles: {len(profiles)}")
        print(f"   Responses: {len(responses)}")
        print(f"   Completed Sessions: {len(sessions)}")
        
        for profile in profiles:
            session_id = profile[0]
            print(f"\n📋 Profile: {profile[1]} - {profile[2]} ({session_id})")
            
            # Show responses for this profile
            session_responses = [r for r in responses if r[1] == session_id]
            if session_responses:
                print(f"   💬 Responses: {len(session_responses)}")
                for i, resp in enumerate(session_responses, 1):
                    print(f"      {i}. Q: {resp[2][:60]}...")
                    print(f"         A: {resp[3][:80]}...")
                    try:
                        eval_data = json.loads(resp[4])
                        if 'scores' in eval_data:
                            print(f"         Scores: {eval_data['scores']}")
                    except:
                        pass
    
    conn.close()

if __name__ == "__main__":
    view_recent_interviews()
