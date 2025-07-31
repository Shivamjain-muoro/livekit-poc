#!/usr/bin/env python3
"""
Script to check and display interview database contents
"""

def get_db_path():
    """Get the correct database path"""
    import os
    db_path = os.path.join('database', 'interview_sessions.db')
    if not os.path.exists(db_path):
        db_path = 'interview_sessions.db'  # Fallback
    return db_path

import sqlite3
import json
from datetime import datetime

def check_database():
    print("🔍 Checking Interview Database...")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Check what tables exist
        print("📋 Available Tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("   ⚠️ No tables found in database")
            conn.close()
            return
        
        for table in tables:
            print(f"   ✅ {table[0]}")
        
        print("\n" + "=" * 50)
        
        # Check candidate_profiles table
        print("👤 CANDIDATE PROFILES:")
        try:
            cursor.execute("SELECT * FROM candidate_profiles ORDER BY created_at DESC")
            profiles = cursor.fetchall()
            
            if profiles:
                print(f"   📊 Found {len(profiles)} candidate profiles:")
                for profile in profiles:
                    print(f"   🆔 Session ID: {profile[0]}")
                    print(f"   👤 Name: {profile[1]}")
                    print(f"   💼 Position: {profile[2]}")
                    print(f"   📈 Experience: {profile[3]}")
                    print(f"   🛠️ Skills: {profile[4]}")
                    print(f"   📅 Created: {profile[6]}")
                    print(f"   ---")
            else:
                print("   ⚠️ No candidate profiles found")
        except sqlite3.OperationalError as e:
            print(f"   ❌ Error accessing candidate_profiles: {e}")
        
        print("\n" + "=" * 50)
        
        # Check interview_responses table
        print("💬 INTERVIEW RESPONSES:")
        try:
            cursor.execute("SELECT * FROM interview_responses ORDER BY timestamp DESC")
            responses = cursor.fetchall()
            
            if responses:
                print(f"   📊 Found {len(responses)} interview responses:")
                for response in responses:
                    print(f"   🆔 Response ID: {response[0]}")
                    print(f"   📝 Session ID: {response[1]}")
                    print(f"   ❓ Question: {response[2][:100]}...")
                    print(f"   💬 Response: {response[3][:100]}...")
                    print(f"   ⭐ Evaluation: {response[4][:100]}...")
                    print(f"   ⏰ Timestamp: {response[5]}")
                    print(f"   ---")
            else:
                print("   ⚠️ No interview responses found")
        except sqlite3.OperationalError as e:
            print(f"   ❌ Error accessing interview_responses: {e}")
        
        print("\n" + "=" * 50)
        
        # Check interview_sessions table
        print("📋 INTERVIEW SESSIONS:")
        try:
            cursor.execute("SELECT * FROM interview_sessions ORDER BY completed_at DESC")
            sessions = cursor.fetchall()
            
            if sessions:
                print(f"   📊 Found {len(sessions)} completed interview sessions:")
                for session in sessions:
                    print(f"   🆔 Session ID: {session[0]}")
                    print(f"   📊 Overall Assessment: {session[1][:200]}...")
                    print(f"   📈 Status: {session[2]}")
                    print(f"   ✅ Completed: {session[3]}")
                    print(f"   📝 Total Responses: {session[4]}")
                    print(f"   ---")
            else:
                print("   ⚠️ No completed interview sessions found")
        except sqlite3.OperationalError as e:
            print(f"   ❌ Error accessing interview_sessions: {e}")
        
        # Summary statistics
        print("\n" + "=" * 50)
        print("📊 DATABASE SUMMARY:")
        
        try:
            cursor.execute("SELECT COUNT(*) FROM candidate_profiles")
            profile_count = cursor.fetchone()[0]
            print(f"   👤 Total Candidates: {profile_count}")
            
            cursor.execute("SELECT COUNT(*) FROM interview_responses")
            response_count = cursor.fetchone()[0]
            print(f"   💬 Total Responses: {response_count}")
            
            cursor.execute("SELECT COUNT(*) FROM interview_sessions WHERE status='completed'")
            completed_count = cursor.fetchone()[0]
            print(f"   ✅ Completed Sessions: {completed_count}")
            
        except sqlite3.OperationalError as e:
            print(f"   ❌ Error getting summary: {e}")
        
        conn.close()
        print("\n✅ Database check completed!")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database()
