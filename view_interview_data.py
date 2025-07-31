#!/usr/bin/env python3
"""
Script to display detailed interview data with full responses and evaluations
"""

import sqlite3
import json
from datetime import datetime

def display_detailed_interview_data():
    print("📋 DETAILED INTERVIEW DATA VIEWER")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect('interview_sessions.db')
        cursor = conn.cursor()
        
        # Get all sessions with their profiles
        cursor.execute("""
            SELECT 
                cp.session_id, cp.name, cp.position, cp.experience_level, cp.skills,
                cp.interview_type, cp.created_at,
                ise.overall_assessment, ise.status, ise.completed_at, ise.total_responses
            FROM candidate_profiles cp
            LEFT JOIN interview_sessions ise ON cp.session_id = ise.session_id
            ORDER BY cp.created_at DESC
        """)
        
        sessions = cursor.fetchall()
        
        for session in sessions:
            session_id = session[0]
            print(f"\n🎯 SESSION: {session_id}")
            print("=" * 80)
            
            # Display candidate profile
            print("👤 CANDIDATE PROFILE:")
            print(f"   📝 Name: {session[1]}")
            print(f"   💼 Position: {session[2]}")
            print(f"   📈 Experience Level: {session[3]}")
            print(f"   🛠️ Skills: {session[4]}")
            print(f"   📋 Interview Type: {session[5]}")
            print(f"   📅 Profile Created: {session[6]}")
            
            # Display session completion info
            if session[7]:  # If overall_assessment exists
                print(f"\n✅ INTERVIEW COMPLETION:")
                print(f"   📊 Status: {session[8]}")
                print(f"   📅 Completed At: {session[9]}")
                print(f"   📝 Total Responses: {session[10]}")
                print(f"   🎯 Overall Assessment:")
                print(f"      {session[7]}")
            else:
                print(f"\n⚠️ INTERVIEW STATUS: Not completed or no completion data")
            
            # Get all responses for this session
            print(f"\n💬 DETAILED RESPONSES:")
            cursor.execute("""
                SELECT question, response, evaluation, timestamp 
                FROM interview_responses 
                WHERE session_id = ? 
                ORDER BY timestamp
            """, (session_id,))
            
            responses = cursor.fetchall()
            
            if responses:
                for i, (question, response, evaluation, timestamp) in enumerate(responses, 1):
                    print(f"\n   📝 QUESTION {i}:")
                    print(f"      ❓ {question}")
                    print(f"      ⏰ Asked at: {timestamp}")
                    
                    print(f"\n   💭 CANDIDATE RESPONSE:")
                    print(f"      {response}")
                    
                    print(f"\n   ⭐ EVALUATION:")
                    # Try to parse evaluation as JSON for better formatting
                    try:
                        eval_data = json.loads(evaluation)
                        print(f"      📊 Feedback: {eval_data.get('feedback', 'No feedback')}")
                        
                        if 'scores' in eval_data:
                            print(f"      🎯 Scores:")
                            for criteria, score in eval_data['scores'].items():
                                print(f"         • {criteria}: {score}")
                        
                        if 'follow_up_question' in eval_data and eval_data['follow_up_question']:
                            print(f"      ❓ Follow-up: {eval_data['follow_up_question']}")
                            
                    except (json.JSONDecodeError, TypeError):
                        # If not JSON, display as plain text
                        print(f"      {evaluation}")
                    
                    print(f"   {'-' * 60}")
            else:
                print("   ⚠️ No responses found for this session")
            
            print("\n" + "=" * 80)
        
        conn.close()
        print("\n✅ Detailed interview data display completed!")
        
    except Exception as e:
        print(f"❌ Error displaying interview data: {e}")

def show_session_menu():
    print("\n📋 INTERVIEW DATA VIEWER MENU")
    print("=" * 40)
    print("1. View all interview data (detailed)")
    print("2. View specific session by ID")
    print("3. View only completed sessions")
    print("4. Exit")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            display_detailed_interview_data()
        elif choice == "2":
            session_id = input("Enter session ID: ").strip()
            display_specific_session(session_id)
        elif choice == "3":
            display_completed_sessions_only()
        elif choice == "4":
            print("👋 Goodbye!")
            return
        else:
            print("❌ Invalid choice. Please enter 1-4.")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

def display_specific_session(session_id):
    print(f"\n🔍 SEARCHING FOR SESSION: {session_id}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('interview_sessions.db')
        cursor = conn.cursor()
        
        # Check if session exists
        cursor.execute("SELECT COUNT(*) FROM candidate_profiles WHERE session_id = ?", (session_id,))
        if cursor.fetchone()[0] == 0:
            print(f"❌ Session '{session_id}' not found!")
            conn.close()
            return
        
        # Display just this session using the same logic
        cursor.execute("""
            SELECT 
                cp.session_id, cp.name, cp.position, cp.experience_level, cp.skills,
                cp.interview_type, cp.created_at,
                ise.overall_assessment, ise.status, ise.completed_at, ise.total_responses
            FROM candidate_profiles cp
            LEFT JOIN interview_sessions ise ON cp.session_id = ise.session_id
            WHERE cp.session_id = ?
        """, (session_id,))
        
        session = cursor.fetchone()
        if session:
            # Use the same display logic as above for this single session
            print(f"\n🎯 SESSION: {session[0]}")
            print("=" * 60)
            # ... (rest of display logic same as above)
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error displaying session: {e}")

def display_completed_sessions_only():
    print("\n✅ COMPLETED SESSIONS ONLY")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect('interview_sessions.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, overall_assessment, completed_at, total_responses
            FROM interview_sessions 
            WHERE status = 'completed'
            ORDER BY completed_at DESC
        """)
        
        sessions = cursor.fetchall()
        
        if sessions:
            for session in sessions:
                print(f"\n🎯 Session: {session[0]}")
                print(f"   📅 Completed: {session[2]}")
                print(f"   📝 Responses: {session[3]}")
                print(f"   📊 Assessment: {session[1][:200]}...")
                print("   " + "-" * 50)
        else:
            print("⚠️ No completed sessions found")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Error displaying completed sessions: {e}")

if __name__ == "__main__":
    display_detailed_interview_data()
