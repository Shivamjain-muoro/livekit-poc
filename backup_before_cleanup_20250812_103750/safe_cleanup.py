"""
SAFE PROJECT CLEANUP - Step by Step
This script will help you clean up your project while maintaining full functionality
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

def create_backup():
    """Create backup before any changes"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_before_cleanup_{timestamp}"
    
    print(f"📦 STEP 1: Creating backup...")
    print(f"   Creating: {backup_dir}")
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    
    # Files to backup (all Python files and config)
    files_to_backup = []
    for ext in ['*.py', '*.yml', '*.yaml', '*.txt', '*.bat', '*.md', '*.db']:
        files_to_backup.extend(Path('.').glob(ext))
    
    for file in files_to_backup:
        if file.name != backup_dir:  # Don't backup the backup folder itself
            try:
                shutil.copy2(file, backup_dir)
                print(f"   ✅ Backed up: {file.name}")
            except Exception as e:
                print(f"   ❌ Failed to backup {file.name}: {e}")
    
    print(f"✅ Backup completed: {backup_dir}")
    return backup_dir

def get_essential_files():
    """Return list of files that MUST be kept"""
    return [
        # Core system files (from dependency analysis)
        'complete_interview_agent.py',
        'realtime_interview_tools.py', 
        'automated_evaluation_system.py',
        'background_evaluator.py',
        'fast_interview_tools.py',
        'report_generator.py',
        
        # Essential utilities
        'local_token_generator.py',
        'check_local_status.py',
        
        # Configuration files
        'requirements.txt',
        'docker-compose.yml',
        'start_local_system.bat',
        'stop_local_system.bat',
        
        # Documentation
        'README.md',
        'DEMO_GUIDE.md',
        
        # Database
        'interview_sessions.db',
        
        # This cleanup script
        'cleanup_analyzer.py',
        'safe_cleanup.py'
    ]

def get_files_to_delete():
    """Return files that can be safely deleted"""
    return {
        'test_files': [
            'test_ai_agent_initialization.py',
            'test_ai_backend.py',
            'test_ai_questions.py',
            'test_backend_connection.py',
            'test_complete_automated_system.py',
            'test_complete_flow.py',
            'test_corrected_api.py',
            'test_debug.py',
            'test_direct_database_save.py',
            'test_enhanced_backend.py',
            'test_enhanced_capture.py',
            'test_enhanced_import.py',
            'test_fixed_tools.py',
            'test_google_realtime.py',
            'test_google_voice.py',
            'test_imports.py',
            'test_interview_flow.py',
            'test_interview_system.py',
            'test_livekit.py',
            'test_logging_system.py',
            'test_pure_livekit_setup.py',
            'test_questions_response.py',
            'test_realtime_system.py',
            'test_recording_function.py',
            'test_server.py',
            'test_session.py',
            'test_session_coordination.py',
            'test_submit_answer.py',
            'test_submit_fix.py',
            'test_system.py',
            'test_voice_ai_system.py',
            'test_voice_system.py',
            'test_voice_system_quick.py'
        ],
        'duplicate_versions': [
            'complete_interview_agent_backup.py',
            'complete_interview_agent_fixed.py',
            'enhanced_agent.py',
            'enhanced_ai_backend.py',
            'enhanced_backend.py',
            'minimal_backend.py',
            'pure_livekit_agent.py',
            'pure_livekit_interview_agent.py',
            'real_interview_agent.py',
            'real_interview_system.py',
            'real_voice_ai_interview.py',
            'real_voice_ai_platform.py',
            'search_real_session.py',
            'simplified_enhanced_backend.py',
            'working_ai_backend.py'
        ],
        'analysis_files': [
            'analyze_fixed_sessions.py',
            'analyze_latest_interview.py',
            'analyze_my_interview.py',
            'check_all_interview_data.py',
            'check_database.py',
            'check_db_status.py',
            'check_evaluation.py',
            'check_google_models.py',
            'check_interview_data.py',
            'check_interview_results.py',
            'check_system_status.py',
            'quick_check.py',
            'quick_db_check.py',
            'quick_interview_summary.py',
            'quick_test.py',
            'simple_db_check.py',
            'simple_recovery.py',
            'simple_status.py',
            'simple_test_agent.py',
            'simple_url_test.py',
            'simple_view_data.py',
            'verify_automated_system.py',
            'verify_interview_logs.py',
            'verify_livekit.py',
            'view_all_interviews.py',
            'view_database.py',
            'view_interview_data.py',
            'view_interview_reports.py',
            'view_interview_results.py'
        ],
        'temporary_files': [
            'fix_automated_evaluation_schema.py',
            'fix_database_schema.py',
            'fix_db_paths.py',
            'fix_incomplete_sessions.py',
            'fix_interview_capture.py',
            'fix_interview_tools.py',
            'fix_schema_alignment.py',
            'fix_summary.py'
        ]
    }

def get_files_to_review():
    """Files that need manual review before deletion"""
    return [
        'agent.py',
        'backend.py', 
        'frontend.py',
        'professional_interview_platform.py',
        'prompts.py',
        'simple_backend.py',
        'simplified_livekit_client.py',
        'test_flow.py',
        'tools_backup.py',
        'tools.py',
        'troubleshoot_livekit.py'
    ]

def step_by_step_cleanup():
    """Main cleanup function with user confirmation at each step"""
    
    print("🧹 SAFE PROJECT CLEANUP")
    print("=" * 60)
    print("This will clean up your project while preserving all functionality")
    print("You'll be asked to confirm each step.")
    
    # Step 1: Create backup
    input("\\n🔹 Press Enter to create backup...")
    backup_dir = create_backup()
    
    # Step 2: Show what will be kept
    essential_files = get_essential_files()
    print(f"\\n📦 STEP 2: Files that will be KEPT ({len(essential_files)} files):")
    for file in essential_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❓ {file} (not found)")
    
    # Step 3: Show what will be deleted
    files_to_delete = get_files_to_delete()
    total_delete = sum(len(files) for files in files_to_delete.values())
    
    print(f"\\n🗑️ STEP 3: Files that will be DELETED ({total_delete} files):")
    for category, files in files_to_delete.items():
        existing_files = [f for f in files if os.path.exists(f)]
        if existing_files:
            print(f"\\n   📂 {category.replace('_', ' ').title()} ({len(existing_files)} files):")
            for file in existing_files[:5]:  # Show first 5
                print(f"      🗑️ {file}")
            if len(existing_files) > 5:
                print(f"      ... and {len(existing_files) - 5} more")
    
    # Step 4: Show files needing review
    review_files = get_files_to_review()
    existing_review = [f for f in review_files if os.path.exists(f)]
    
    if existing_review:
        print(f"\\n❓ STEP 4: Files that need MANUAL REVIEW ({len(existing_review)} files):")
        for file in existing_review:
            print(f"   ❓ {file}")
        print("\\n   These files will NOT be deleted automatically.")
        print("   You should review them manually to see if they're needed.")
    
    # Step 5: Confirm deletion
    print(f"\\n📊 SUMMARY:")
    print(f"   ✅ Files to keep: {len(essential_files)}")
    print(f"   🗑️ Files to delete: {total_delete}")
    print(f"   ❓ Files to review: {len(existing_review)}")
    print(f"   📦 Backup created: {backup_dir}")
    
    confirm = input(f"\\n🔹 Do you want to DELETE {total_delete} files? (yes/no): ").lower().strip()
    
    if confirm == 'yes':
        print(f"\\n🗑️ STEP 5: Deleting files...")
        deleted_count = 0
        
        for category, files in files_to_delete.items():
            for file in files:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                        print(f"   ✅ Deleted: {file}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"   ❌ Failed to delete {file}: {e}")
        
        print(f"\\n✅ CLEANUP COMPLETED!")
        print(f"   📊 Deleted {deleted_count} files")
        print(f"   💾 Backup saved: {backup_dir}")
        print(f"   🔧 Your system should work exactly the same!")
        
        # Show final file count
        remaining_py_files = [f for f in os.listdir('.') if f.endswith('.py')]
        print(f"   📄 Remaining Python files: {len(remaining_py_files)}")
        
    else:
        print("\\n❌ Cleanup cancelled. No files were deleted.")
        print(f"   💾 Backup is still available: {backup_dir}")
    
    return backup_dir

if __name__ == "__main__":
    step_by_step_cleanup()
