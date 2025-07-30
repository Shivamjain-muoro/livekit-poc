#!/usr/bin/env python3
"""
Database initialization script for the Interview System
Creates all necessary tables with proper schema
"""

import sqlite3
import os
from datetime import datetime

def init_database():
    """Initialize the database with proper schema"""
    
    # Remove existing database if it exists
    if os.path.exists('interview_sessions.db'):
        os.remove('interview_sessions.db')
    
    # Create new database connection
    conn = sqlite3.connect('interview_sessions.db')
    cursor = conn.cursor()
    
    # Create sessions table (not interview_sessions)
    cursor.execute('''
        CREATE TABLE sessions (
            id TEXT PRIMARY KEY,
            participant_name TEXT NOT NULL,
            participant_email TEXT NOT NULL,
            position TEXT NOT NULL,
            experience_level TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'created',
            room_name TEXT NOT NULL,
            current_question_index INTEGER DEFAULT 0,
            total_questions INTEGER DEFAULT 0,
            start_time TEXT,
            end_time TEXT,
            pause_duration INTEGER DEFAULT 0,
            interview_data TEXT DEFAULT '{}',
            skills TEXT DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    # Create questions table
    cursor.execute('''
        CREATE TABLE questions (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            question_text TEXT NOT NULL,
            question_type TEXT NOT NULL,
            difficulty_level INTEGER NOT NULL,
            expected_duration INTEGER NOT NULL,
            order_index INTEGER NOT NULL,
            is_asked BOOLEAN DEFAULT FALSE,
            asked_at TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')
    
    # Create answers table
    cursor.execute('''
        CREATE TABLE answers (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            question_id TEXT NOT NULL,
            answer_text TEXT NOT NULL,
            duration INTEGER NOT NULL,
            submitted_at TEXT NOT NULL,
            audio_url TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions (id),
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    ''')
    
    # Create feedback table
    cursor.execute('''
        CREATE TABLE feedback (
            id TEXT PRIMARY KEY,
            answer_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            score INTEGER NOT NULL,
            feedback_text TEXT NOT NULL,
            criteria_scores TEXT DEFAULT '{}',
            strengths TEXT DEFAULT '[]',
            improvements TEXT DEFAULT '[]',
            evaluated_at TEXT NOT NULL,
            FOREIGN KEY (answer_id) REFERENCES answers (id),
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX idx_sessions_status ON sessions(status)')
    cursor.execute('CREATE INDEX idx_questions_session ON questions(session_id)')
    cursor.execute('CREATE INDEX idx_answers_session ON answers(session_id)')
    cursor.execute('CREATE INDEX idx_feedback_session ON feedback(session_id)')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database initialized successfully with proper schema!")
    print("Tables created: sessions, questions, answers, feedback")

if __name__ == "__main__":
    init_database()
