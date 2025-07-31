#!/usr/bin/env python3

import sqlite3
from datetime import datetime

def check_all_interview_data():
    """Check all interview data across all tables"""
    
    conn = sqlite3.connect('interview_sessions.db')
    cursor = conn.cursor()
    
    print("=== DATABASE SCHEMA ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Available tables:", [t[0] for t in tables])
    
    print("\n=== SESSIONS TABLE (Recent first) ===")
    try:
        cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC LIMIT 10")
        sessions = cursor.fetchall()
        if sessions:
            for i, session in enumerate(sessions, 1):
                print(f"{i}. Session ID: {session[0]}")
                print(f"   Created: {session[2] if len(session) > 2 else 'Unknown'}")
                print(f"   Status: {session[1] if len(session) > 1 else 'Unknown'}")
                print()
        else:
            print("No sessions found in sessions table")
    except Exception as e:
        print(f"Error reading sessions table: {e}")
    
    print("\n=== QUESTIONS TABLE (Recent first) ===")
    try:
        cursor.execute("SELECT * FROM questions ORDER BY created_at DESC LIMIT 10")
        questions = cursor.fetchall()
        if questions:
            for i, question in enumerate(questions, 1):
                print(f"{i}. Question ID: {question[0]}")
                print(f"   Session: {question[1] if len(question) > 1 else 'Unknown'}")
                print(f"   Question: {question[2][:100] if len(question) > 2 and question[2] else 'No question'}...")
                print(f"   Created: {question[3] if len(question) > 3 else 'Unknown'}")
                print()
        else:
            print("No questions found in questions table")
    except Exception as e:
        print(f"Error reading questions table: {e}")
    
    print("\n=== ANSWERS TABLE (Recent first) ===")
    try:
        cursor.execute("SELECT * FROM answers ORDER BY created_at DESC LIMIT 10")
        answers = cursor.fetchall()
        if answers:
            for i, answer in enumerate(answers, 1):
                print(f"{i}. Answer ID: {answer[0]}")
                print(f"   Question ID: {answer[1] if len(answer) > 1 else 'Unknown'}")
                print(f"   Answer: {answer[2][:150] if len(answer) > 2 and answer[2] else 'No answer'}...")
                print(f"   Created: {answer[3] if len(answer) > 3 else 'Unknown'}")
                print()
        else:
            print("No answers found in answers table")
    except Exception as e:
        print(f"Error reading answers table: {e}")
    
    print("\n=== FEEDBACK TABLE (Recent first) ===")
    try:
        cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC LIMIT 10")
        feedback = cursor.fetchall()
        if feedback:
            for i, fb in enumerate(feedback, 1):
                print(f"{i}. Feedback ID: {fb[0]}")
                print(f"   Answer ID: {fb[1] if len(fb) > 1 else 'Unknown'}")
                print(f"   Feedback: {fb[2][:150] if len(fb) > 2 and fb[2] else 'No feedback'}...")
                print(f"   Created: {fb[3] if len(fb) > 3 else 'Unknown'}")
                print()
        else:
            print("No feedback found in feedback table")
    except Exception as e:
        print(f"Error reading feedback table: {e}")
    
    print("\n=== NEW TABLES DATA ===")
    print("Candidate Profiles:")
    cursor.execute("SELECT * FROM candidate_profiles ORDER BY created_at DESC")
    profiles = cursor.fetchall()
    for profile in profiles:
        print(f"  Session: {profile[0]}, Name: {profile[1]}, Position: {profile[2]}")
    
    print("\nInterview Responses:")
    cursor.execute("SELECT COUNT(*) FROM interview_responses")
    response_count = cursor.fetchone()[0]
    print(f"  Total responses: {response_count}")
    
    print("\nCompleted Sessions:")
    cursor.execute("SELECT * FROM interview_sessions ORDER BY completed_at DESC")
    completed = cursor.fetchall()
    for session in completed:
        print(f"  Session: {session[0]}, Status: {session[2]}, Responses: {session[4]}")
    
    conn.close()

if __name__ == "__main__":
    check_all_interview_data()
