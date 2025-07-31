#!/usr/bin/env python3
"""
Interactive Interview Data Query Tool
"""

import sqlite3
import json
from datetime import datetime

def get_session_by_id(session_id):
    """Get detailed information for a specific session"""
    try:
        conn = sqlite3.connect('interview_sessions.db')
        cursor = conn.cursor()
        
        # Get profile
        cursor.execute("SELECT * FROM candidate_profiles WHERE session_id = ?", (session_id,))
        profile = cursor.fetchone()
        
        if not profile:
            print(f"❌ Session '{session_id}' not found!")
            return
        
        # Get completion data
        cursor.execute("SELECT * FROM interview_sessions WHERE session_id = ?", (session_id,))
        session_data = cursor.fetchone()
        
        # Get responses
        cursor.execute("SELECT * FROM interview_responses WHERE session_id = ? ORDER BY timestamp", (session_id,))
        responses = cursor.fetchall()
        
        # Display results
        print(f"\n📋 COMPLETE INTERVIEW REPORT")
        print(f"Session ID: {session_id}")
        print("=" * 60)
        
        print(f"Candidate: {profile[1]}")
        print(f"Position: {profile[2]}")
        print(f"Experience: {profile[3]}")
        print(f"Skills: {profile[4]}")
        print(f"Interview Type: {profile[5]}")
        
        if session_data:
            print(f"\nStatus: {session_data[2]}")
            print(f"Completed: {session_data[3]}")
            print(f"Total Questions: {session_data[4]}")
            print(f"\nOverall Assessment:")
            print(f"{session_data[1]}")
        
        print(f"\n📝 Questions & Responses ({len(responses)} total):")
        for i, response in enumerate(responses, 1):
            print(f"\n{i}. Q: {response[2]}")
            print(f"   A: {response[3]}")
            print(f"   Evaluation: {response[4]}")
            print(f"   Time: {response[5]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def list_all_sessions():
    """List all interview sessions with basic info"""
    try:
        conn = sqlite3.connect('interview_sessions.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT cp.session_id, cp.name, cp.position, cp.created_at,
                   ise.status, ise.total_responses
            FROM candidate_profiles cp
            LEFT JOIN interview_sessions ise ON cp.session_id = ise.session_id
            ORDER BY cp.created_at DESC
        """)
        
        sessions = cursor.fetchall()
        
        print("\n📋 ALL INTERVIEW SESSIONS")
        print("=" * 80)
        print(f"{'Session ID':<15} {'Name':<20} {'Position':<15} {'Status':<10} {'Responses':<10} {'Date'}")
        print("-" * 80)
        
        for session in sessions:
            status = session[4] if session[4] else "Incomplete"
            responses = session[5] if session[5] else 0
            date = session[3][:10] if session[3] else "Unknown"
            
            print(f"{session[0]:<15} {session[1]:<20} {session[2]:<15} {status:<10} {responses:<10} {date}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def search_by_date(date_str):
    """Search sessions by date (YYYY-MM-DD format)"""
    try:
        conn = sqlite3.connect('interview_sessions.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, name, position, created_at
            FROM candidate_profiles 
            WHERE DATE(created_at) = ?
            ORDER BY created_at
        """, (date_str,))
        
        sessions = cursor.fetchall()
        
        if sessions:
            print(f"\n📅 Sessions from {date_str}:")
            for session in sessions:
                print(f"   🎯 {session[0]} - {session[1]} ({session[2]})")
        else:
            print(f"❌ No sessions found for {date_str}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    while True:
        print("\n🎯 INTERVIEW DATA QUERY TOOL")
        print("=" * 40)
        print("1. List all sessions")
        print("2. View specific session details")
        print("3. Search by date (YYYY-MM-DD)")
        print("4. Export session to JSON")
        print("5. Exit")
        
        try:
            choice = input("\nChoose option (1-5): ").strip()
            
            if choice == "1":
                list_all_sessions()
            
            elif choice == "2":
                session_id = input("Enter session ID: ").strip()
                get_session_by_id(session_id)
            
            elif choice == "3":
                date_str = input("Enter date (YYYY-MM-DD): ").strip()
                search_by_date(date_str)
            
            elif choice == "4":
                session_id = input("Enter session ID to export: ").strip()
                export_to_json(session_id)
            
            elif choice == "5":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

def export_to_json(session_id):
    """Export session data to JSON file"""
    try:
        conn = sqlite3.connect('interview_sessions.db')
        cursor = conn.cursor()
        
        # Get all data for session
        cursor.execute("SELECT * FROM candidate_profiles WHERE session_id = ?", (session_id,))
        profile = cursor.fetchone()
        
        if not profile:
            print(f"❌ Session '{session_id}' not found!")
            return
        
        cursor.execute("SELECT * FROM interview_sessions WHERE session_id = ?", (session_id,))
        session_data = cursor.fetchone()
        
        cursor.execute("SELECT * FROM interview_responses WHERE session_id = ? ORDER BY timestamp", (session_id,))
        responses = cursor.fetchall()
        
        # Build JSON structure
        export_data = {
            "session_id": session_id,
            "candidate_profile": {
                "name": profile[1],
                "position": profile[2],
                "experience_level": profile[3],
                "skills": profile[4],
                "interview_type": profile[5],
                "created_at": profile[6]
            },
            "session_completion": {
                "overall_assessment": session_data[1] if session_data else None,
                "status": session_data[2] if session_data else "incomplete",
                "completed_at": session_data[3] if session_data else None,
                "total_responses": session_data[4] if session_data else len(responses)
            },
            "responses": []
        }
        
        for response in responses:
            export_data["responses"].append({
                "question": response[2],
                "candidate_response": response[3],
                "evaluation": response[4],
                "timestamp": response[5]
            })
        
        # Save to file
        filename = f"interview_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported session '{session_id}' to {filename}")
        conn.close()
        
    except Exception as e:
        print(f"❌ Error exporting: {e}")

if __name__ == "__main__":
    main()
