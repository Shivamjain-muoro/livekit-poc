#!/usr/bin/env python3
"""
Fix Database Schema - Align with Evaluation Code
"""

import sqlite3
import os

def fix_schema_alignment():
    """Fix database schema to align with evaluation code expectations"""
    
    print("🔧 FIXING DATABASE SCHEMA ALIGNMENT...")
    print("="*60)
    
    db_path = os.path.join("database", "interview_evaluations.db")
    
    # Expected columns by the evaluation code
    expected_columns = [
        "correctness_score",
        "completeness_score", 
        "clarity_score",
        "skill_relevance_score",
        "fluency_score",
        "confidence_score",
        "sentiment_positive",
        "sentiment_neutral", 
        "sentiment_negative",
        "key_skills_demonstrated",
        "areas_of_concern",
        "follow_up_suggestions",
        "processing_time",
        "evaluation_completed"
    ]
    
    with sqlite3.connect(db_path) as conn:
        # Get current columns
        cursor = conn.execute("PRAGMA table_info(interview_exchanges)")
        current_columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        print(f"📊 Current columns: {len(current_columns)}")
        for col, type_info in current_columns.items():
            print(f"   - {col} ({type_info})")
        print()
        
        # Add missing columns
        missing_columns = []
        for col in expected_columns:
            if col not in current_columns:
                missing_columns.append(col)
        
        if missing_columns:
            print(f"➕ Adding {len(missing_columns)} missing columns:")
            for col in missing_columns:
                try:
                    if col in ["key_skills_demonstrated", "areas_of_concern", "follow_up_suggestions"]:
                        conn.execute(f"ALTER TABLE interview_exchanges ADD COLUMN {col} TEXT")
                    elif col == "evaluation_completed":
                        conn.execute(f"ALTER TABLE interview_exchanges ADD COLUMN {col} BOOLEAN DEFAULT 0")
                    else:
                        conn.execute(f"ALTER TABLE interview_exchanges ADD COLUMN {col} REAL DEFAULT 0")
                    print(f"   ✅ Added: {col}")
                except sqlite3.Error as e:
                    print(f"   ❌ Error adding {col}: {e}")
            
            conn.commit()
            print(f"   💾 Changes committed to database")
        else:
            print("   ✅ All expected columns already exist")
        
        print()
        
        # Verify final schema
        print("📊 FINAL SCHEMA:")
        cursor = conn.execute("PRAGMA table_info(interview_exchanges)")
        final_columns = cursor.fetchall()
        
        evaluation_cols = []
        other_cols = []
        
        for row in final_columns:
            col_name = row[1]
            col_type = row[2]
            if col_name in expected_columns:
                evaluation_cols.append(f"{col_name} ({col_type})")
            else:
                other_cols.append(f"{col_name} ({col_type})")
        
        print("   🎯 EVALUATION COLUMNS:")
        for col in evaluation_cols:
            print(f"      ✅ {col}")
        
        print("   📋 OTHER COLUMNS:")
        for col in other_cols:
            print(f"      • {col}")
        
        print(f"\n✅ Schema alignment completed!")
        print(f"   📊 Total columns: {len(final_columns)}")
        print(f"   🎯 Evaluation columns: {len(evaluation_cols)}")
        print(f"   📋 Other columns: {len(other_cols)}")
        
        # Test evaluation column access
        print("\n🧪 TESTING EVALUATION COLUMN ACCESS:")
        try:
            conn.execute("SELECT correctness_score, completeness_score, clarity_score FROM interview_exchanges LIMIT 1")
            print("   ✅ Can access correctness_score, completeness_score, clarity_score")
        except sqlite3.Error as e:
            print(f"   ❌ Error accessing evaluation columns: {e}")
        
        try:
            conn.execute("SELECT sentiment_positive, evaluation_completed FROM interview_exchanges LIMIT 1")
            print("   ✅ Can access sentiment_positive, evaluation_completed")
        except sqlite3.Error as e:
            print(f"   ❌ Error accessing sentiment columns: {e}")

if __name__ == "__main__":
    fix_schema_alignment()
