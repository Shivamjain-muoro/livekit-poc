#!/usr/bin/env python3
"""
Quick Database Check - See Current Data
"""

import sqlite3
import os

def quick_db_check():
    """Quick check of database content"""
    
    db_path = os.path.join("database", "interview_evaluations.db")
    
    with sqlite3.connect(db_path) as conn:
        print("📊 TABLES:")
        for row in conn.execute('SELECT name FROM sqlite_master WHERE type="table"'):
            print(f"   - {row[0]}")
        
        print("\n📝 RECENT EXCHANGES:")
        try:
            for row in conn.execute('SELECT session_id, question, response FROM interview_exchanges ORDER BY id DESC LIMIT 3'):
                print(f"   • {row[0]}: {row[1][:30]}... → {row[2][:30]}...")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n🔍 EXCHANGE TABLE SCHEMA:")
        for row in conn.execute('PRAGMA table_info(interview_exchanges)'):
            print(f"   - {row[1]} ({row[2]})")

if __name__ == "__main__":
    quick_db_check()
