#!/usr/bin/env python3
"""
Fix incomplete interview sessions that weren't properly closed
"""

import sqlite3
import os
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    db_path = os.path.join("database", "interview_evaluations.db")
    return sqlite3.connect(db_path)

def fix_incomplete_sessions():
    """Fix sessions that are marked as active but should be completed"""
    
    print("🔧 FIXING INCOMPLETE SESSIONS")
    print("=" * 50)
    
    with get_db_connection() as conn:
        # Find all active sessions
        cursor = conn.execute("""
            SELECT session_id, candidate_name, position, start_time, status 
            FROM interview_sessions 
            WHERE status = 'active'
            ORDER BY start_time DESC
        """)
        
        active_sessions = cursor.fetchall()
        
        if not active_sessions:
            print("✅ No incomplete sessions found - all sessions are properly closed")
            return
        
        print(f"📋 Found {len(active_sessions)} incomplete sessions:")
        print()
        
        for session in active_sessions:
            session_id, candidate_name, position, start_time, status = session
            print(f"🔍 Session: {session_id}")
            print(f"   👤 Candidate: {candidate_name}")
            print(f"   💼 Position: {position}")
            print(f"   ⏰ Started: {start_time}")
            print(f"   📊 Status: {status}")
            
            # Check if this session has any interview exchanges
            cursor = conn.execute("""
                SELECT COUNT(*), MAX(timestamp) 
                FROM interview_exchanges 
                WHERE session_id = ?
            """, (session_id,))
            
            exchange_result = cursor.fetchone()
            exchange_count = exchange_result[0] if exchange_result else 0
            last_activity = exchange_result[1] if exchange_result else None
            
            print(f"   💬 Q&A Exchanges: {exchange_count}")
            if last_activity:
                print(f"   🕐 Last Activity: {last_activity}")
            
            # Update session to completed with current timestamp as end time
            end_time = datetime.now().isoformat()
            
            print(f"   🔧 Updating status to 'completed' with end time: {end_time}")
            
            conn.execute("""
                UPDATE interview_sessions 
                SET status = 'completed',
                    end_time = ?
                WHERE session_id = ?
            """, (end_time, session_id))
            
            print(f"   ✅ Session {session_id} marked as completed")
            print()
        
        conn.commit()
        print(f"✅ Successfully fixed {len(active_sessions)} incomplete sessions")

def verify_session_status():
    """Verify the status of all sessions after fix"""
    
    print("\n🔍 VERIFYING SESSION STATUS")
    print("=" * 50)
    
    with get_db_connection() as conn:
        # Get session status summary
        cursor = conn.execute("""
            SELECT status, COUNT(*) 
            FROM interview_sessions 
            GROUP BY status
            ORDER BY status
        """)
        
        status_summary = cursor.fetchall()
        
        print("📊 Session Status Summary:")
        for status, count in status_summary:
            print(f"   {status}: {count} sessions")
        
        # Show recent sessions
        print("\n📋 Recent Sessions (Last 5):")
        cursor = conn.execute("""
            SELECT session_id, candidate_name, start_time, end_time, status 
            FROM interview_sessions 
            ORDER BY start_time DESC 
            LIMIT 5
        """)
        
        recent_sessions = cursor.fetchall()
        for session in recent_sessions:
            session_id, candidate_name, start_time, end_time, status = session
            print(f"   🗂️  {session_id[:16]}... | {candidate_name} | {start_time[:19]} -> {end_time[:19] if end_time else 'None'} | {status}")

if __name__ == "__main__":
    try:
        fix_incomplete_sessions()
        verify_session_status()
        print("\n🎉 All sessions fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing sessions: {e}")
