#!/usr/bin/env python3
"""
Fix Database Schema for Real-time Interview Tools
Adds missing columns for evaluation metrics
"""

import sqlite3
import os

def fix_database_schema():
    print("🔧 FIXING DATABASE SCHEMA FOR REAL-TIME TOOLS")
    print("=" * 50)
    
    db_path = "database/interview_sessions.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📋 Checking current schema...")
        
        # Check if qa_exchanges table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='qa_exchanges'")
        qa_table_exists = cursor.fetchone()
        
        if not qa_table_exists:
            print("🔨 Creating qa_exchanges table...")
            cursor.execute('''
                CREATE TABLE qa_exchanges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    question TEXT,
                    response TEXT,
                    response_time_ms REAL,
                    timestamp TEXT,
                    evaluation_data TEXT,
                    correctness_score REAL DEFAULT 0,
                    completeness_score REAL DEFAULT 0,
                    clarity_score REAL DEFAULT 0,
                    relevance_score REAL DEFAULT 0,
                    confidence_score REAL DEFAULT 0,
                    fluency_score REAL DEFAULT 0,
                    sentiment_score REAL DEFAULT 0,
                    overall_score REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("✅ qa_exchanges table created")
        else:
            print("✅ qa_exchanges table already exists")
            
            # Check and add missing columns if needed
            cursor.execute("PRAGMA table_info(qa_exchanges)")
            columns = [col[1] for col in cursor.fetchall()]
            
            missing_columns = [
                ('correctness_score', 'REAL DEFAULT 0'),
                ('completeness_score', 'REAL DEFAULT 0'),
                ('clarity_score', 'REAL DEFAULT 0'),
                ('relevance_score', 'REAL DEFAULT 0'),
                ('confidence_score', 'REAL DEFAULT 0'),
                ('fluency_score', 'REAL DEFAULT 0'),
                ('sentiment_score', 'REAL DEFAULT 0'),
                ('overall_score', 'REAL DEFAULT 0')
            ]
            
            for col_name, col_type in missing_columns:
                if col_name not in columns:
                    print(f"🔨 Adding missing column: {col_name}")
                    cursor.execute(f"ALTER TABLE qa_exchanges ADD COLUMN {col_name} {col_type}")
                else:
                    print(f"✅ Column exists: {col_name}")
        
        # Check sessions table in realtime tools format
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='realtime_sessions'")
        realtime_table_exists = cursor.fetchone()
        
        if not realtime_table_exists:
            print("🔨 Creating realtime_sessions table...")
            cursor.execute('''
                CREATE TABLE realtime_sessions (
                    session_id TEXT PRIMARY KEY,
                    candidate_name TEXT,
                    position TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    status TEXT DEFAULT 'active',
                    total_questions INTEGER DEFAULT 0,
                    total_responses INTEGER DEFAULT 0,
                    session_data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("✅ realtime_sessions table created")
        else:
            print("✅ realtime_sessions table already exists")
        
        conn.commit()
        conn.close()
        
        print("\n✅ DATABASE SCHEMA FIXED SUCCESSFULLY!")
        print("🎯 All required columns and tables are now available")
        print("📊 Real-time evaluation system will now work without errors")
        
    except Exception as e:
        print(f"❌ Error fixing schema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_database_schema()
