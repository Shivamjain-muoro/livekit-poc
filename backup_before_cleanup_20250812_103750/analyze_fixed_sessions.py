#!/usr/bin/env python3
"""
Enhanced analysis of the interview sessions including the ones that were just fixed
"""

import sqlite3
import os
import json
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    db_path = os.path.join("database", "interview_evaluations.db")
    return sqlite3.connect(db_path)

def analyze_interview_sessions():
    """Analyze the interview sessions to understand what happened"""
    
    print("📊 COMPREHENSIVE INTERVIEW SESSION ANALYSIS")
    print("=" * 60)
    
    with get_db_connection() as conn:
        # Get all sessions
        cursor = conn.execute("""
            SELECT session_id, candidate_name, position, start_time, end_time, status 
            FROM interview_sessions 
            ORDER BY start_time DESC
        """)
        
        all_sessions = cursor.fetchall()
        
        print(f"📋 Total Sessions Found: {len(all_sessions)}")
        print()
        
        # Analyze the recent actual LiveKit sessions
        livekit_sessions = [s for s in all_sessions if s[0].startswith('interview_') and not s[0].startswith('interview_202')]
        
        print(f"🚀 Recent LiveKit Sessions (interview_XXXXXXXX format): {len(livekit_sessions)}")
        print()
        
        for session in livekit_sessions:
            session_id, candidate_name, position, start_time, end_time, status = session
            
            print(f"🔍 SESSION: {session_id}")
            print(f"   👤 Candidate: {candidate_name}")
            print(f"   💼 Position: {position}")
            print(f"   ⏰ Started: {start_time}")
            print(f"   🏁 Ended: {end_time}")
            print(f"   📊 Status: {status}")
            
            # Calculate duration
            if start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time)
                    end_dt = datetime.fromisoformat(end_time)
                    duration = (end_dt - start_dt).total_seconds() / 60
                    print(f"   ⏱️  Duration: {duration:.1f} minutes")
                except:
                    print(f"   ⏱️  Duration: Unable to calculate")
            
            # Get interview exchanges for this session
            cursor = conn.execute("""
                SELECT question, response, timestamp, response_duration, 
                       relevance_score, clarity_score, depth_score,
                       ai_evaluation, key_points
                FROM interview_exchanges 
                WHERE session_id = ?
                ORDER BY timestamp
            """, (session_id,))
            
            exchanges = cursor.fetchall()
            
            print(f"   💬 Q&A Exchanges: {len(exchanges)}")
            
            if exchanges:
                print(f"   📝 Exchange Details:")
                for i, exchange in enumerate(exchanges, 1):
                    question, response, timestamp, resp_duration, relevance_score, clarity_score, depth_score, ai_eval, key_points = exchange
                    print(f"      {i}. Q: {question[:50]}{'...' if len(question) > 50 else ''}")
                    print(f"         R: {response[:50]}{'...' if len(response) > 50 else ''}")
                    print(f"         ⏱️  Response Time: {resp_duration}s")
                    print(f"         🎯 Scores: Relevance={relevance_score}, Clarity={clarity_score}, Depth={depth_score}")
                    print(f"         🤖 Evaluation: {ai_eval[:50] if ai_eval else 'None'}{'...' if ai_eval and len(ai_eval) > 50 else ''}")
                    print()
            else:
                print(f"   💬 No structured Q&A exchanges found (natural conversation)")
            
            print("-" * 40)
            print()

def identify_issues():
    """Identify the issues with session tracking"""
    
    print("🔎 ISSUE ANALYSIS")
    print("=" * 40)
    
    print("🔍 FINDINGS:")
    print("1. 📊 Sessions were being created but not properly closed")
    print("2. 🤖 AI agent called end_interview_session but with empty session_id")
    print("3. 🔧 The fallback logic in end_interview_session wasn't working properly")
    print("4. 💬 Real conversations happened but weren't captured as structured Q&A")
    print("5. ⚡ Technical performance was excellent (sub-millisecond operations)")
    print()
    
    print("🔧 ROOT CAUSE:")
    print("- LiveKit room names weren't being properly passed as session_ids")
    print("- End session function couldn't identify which session to close")
    print("- Natural conversation wasn't triggering structured evaluation tools")
    print()
    
    print("✅ RESOLUTION:")
    print("- Fixed incomplete sessions by updating their status to 'completed'")
    print("- Need to improve session ID tracking in LiveKit agent")
    print("- Need to enhance AI prompts to capture more structured data")

def recommendations():
    """Provide recommendations for improvement"""
    
    print("\n📋 RECOMMENDATIONS FOR IMPROVEMENT")
    print("=" * 50)
    
    print("1. 🔧 SESSION TRACKING IMPROVEMENTS:")
    print("   - Store room name as session_id in agent startup")
    print("   - Add session context to all tool calls")
    print("   - Implement auto-session discovery for end_interview_session")
    print()
    
    print("2. 🤖 AI BEHAVIOR OPTIMIZATION:")
    print("   - Update prompts to encourage more use of evaluation tools")
    print("   - Add periodic progress checks during conversation")
    print("   - Implement natural transition to structured evaluation")
    print()
    
    print("3. 📊 DATA CAPTURE ENHANCEMENT:")
    print("   - Auto-detect questions and responses in conversation")
    print("   - Background parsing of natural dialogue")
    print("   - Real-time conversation analysis")
    print()
    
    print("4. 🔍 MONITORING & DEBUGGING:")
    print("   - Add more detailed session lifecycle logging")
    print("   - Implement session health checks")
    print("   - Create real-time session monitoring dashboard")

if __name__ == "__main__":
    try:
        analyze_interview_sessions()
        identify_issues()
        recommendations()
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
