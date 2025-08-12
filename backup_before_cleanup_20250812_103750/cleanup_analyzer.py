"""
Project Cleanup Analysis - Find Dependencies and Remove Unnecessary Files
"""

import ast
import os
import re
from pathlib import Path
import shutil
from datetime import datetime

def analyze_imports_in_file(file_path):
    """Extract all imports from a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]
                    imports.add(module_name)
        
        return imports
    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")
        return set()

def find_core_dependencies():
    """Find all dependencies from core files"""
    
    # Core files based on your main agent
    core_files = [
        'complete_interview_agent.py',
        'realtime_interview_tools.py', 
        'automated_evaluation_system.py',
        'fast_interview_tools.py',
        'background_evaluator.py',
        'report_generator.py'
    ]
    
    all_local_imports = set()
    file_dependencies = {}
    
    print("🔍 ANALYZING CORE FILE DEPENDENCIES:")
    print("=" * 50)
    
    for file in core_files:
        if os.path.exists(file):
            imports = analyze_imports_in_file(file)
            file_dependencies[file] = imports
            
            # Find local imports (files in current directory)
            local_imports = []
            for imp in imports:
                if os.path.exists(f"{imp}.py"):
                    local_imports.append(f"{imp}.py")
                    all_local_imports.add(f"{imp}.py")
            
            print(f"📄 {file}:")
            if local_imports:
                for local_imp in local_imports:
                    print(f"   📦 imports: {local_imp}")
            else:
                print(f"   ✅ no local imports")
        else:
            print(f"❌ {file} - NOT FOUND")
    
    print(f"\n🔗 ALL LOCAL DEPENDENCIES FOUND:")
    for dep in sorted(all_local_imports):
        print(f"   ✅ {dep}")
    
    return all_local_imports, file_dependencies

def categorize_all_files():
    """Categorize all files in the project"""
    
    # Get all Python files
    all_files = [f for f in os.listdir('.') if f.endswith('.py')]
    
    # Essential categories
    categories = {
        'core_essential': [
            'complete_interview_agent.py',
            'realtime_interview_tools.py',
            'automated_evaluation_system.py'
        ],
        'imported_dependencies': [],  # Will be filled by dependency analysis
        'utility_tools': [
            'local_token_generator.py',
            'check_local_status.py'
        ],
        'config_files': [
            'docker-compose.yml',
            'requirements.txt',
            'start_local_system.bat',
            'stop_local_system.bat'
        ],
        'test_files': [],
        'duplicate_versions': [],
        'analysis_files': [],
        'temporary_files': [],
        'unknown_files': []
    }
    
    # Categorize files
    for file in all_files:
        if file in categories['core_essential']:
            continue
        elif file.startswith('test_'):
            categories['test_files'].append(file)
        elif file.startswith('check_') and file != 'check_local_status.py':
            categories['analysis_files'].append(file)
        elif file.startswith('analyze_'):
            categories['analysis_files'].append(file)
        elif file.startswith('verify_'):
            categories['analysis_files'].append(file)
        elif file.startswith('view_'):
            categories['analysis_files'].append(file)
        elif file.startswith('quick_'):
            categories['analysis_files'].append(file)
        elif file.startswith('simple_'):
            categories['analysis_files'].append(file)
        elif file.startswith('fix_'):
            categories['temporary_files'].append(file)
        elif '_backup' in file or '_fixed' in file or '_old' in file:
            categories['duplicate_versions'].append(file)
        elif 'complete_interview_agent' in file and file != 'complete_interview_agent.py':
            categories['duplicate_versions'].append(file)
        elif any(keyword in file for keyword in ['enhanced', 'real_', 'pure_', 'minimal_', 'working_']):
            categories['duplicate_versions'].append(file)
        else:
            categories['unknown_files'].append(file)
    
    return categories

def create_backup():
    """Create backup before cleanup"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_before_cleanup_{timestamp}"
    
    print(f"💾 Creating backup: {backup_dir}")
    
    # Create backup
    shutil.copytree('.', backup_dir, ignore=shutil.ignore_patterns(
        '__pycache__', '*.pyc', '.git', 'backup_*', 'node_modules'
    ))
    
    print(f"✅ Backup created: {backup_dir}")
    return backup_dir

def main():
    print("🧹 PROJECT CLEANUP ANALYSIS")
    print("=" * 60)
    
    # Step 1: Find core dependencies
    local_deps, file_deps = find_core_dependencies()
    
    # Step 2: Categorize all files
    categories = categorize_all_files()
    
    # Step 3: Update categories with dependencies
    categories['imported_dependencies'] = list(local_deps)
    
    # Step 4: Remove dependencies from unknown files
    for dep in local_deps:
        if dep in categories['unknown_files']:
            categories['unknown_files'].remove(dep)
    
    print(f"\n📊 FILE CATEGORIZATION:")
    print("=" * 50)
    
    total_files = 0
    for category, files in categories.items():
        if files:
            total_files += len(files)
            status = "🟢" if category in ['core_essential', 'imported_dependencies', 'utility_tools', 'config_files'] else "🟡" if category == 'unknown_files' else "🔴"
            print(f"\n{status} {category.upper().replace('_', ' ')} ({len(files)} files):")
            for file in sorted(files):
                print(f"   📄 {file}")
    
    print(f"\n📈 SUMMARY:")
    print(f"Total files analyzed: {total_files}")
    
    # Cleanup recommendations
    keep_files = categories['core_essential'] + categories['imported_dependencies'] + categories['utility_tools'] + categories['config_files']
    delete_files = categories['test_files'] + categories['duplicate_versions'] + categories['analysis_files'] + categories['temporary_files']
    review_files = categories['unknown_files']
    
    print(f"\n🎯 CLEANUP RECOMMENDATIONS:")
    print(f"✅ KEEP: {len(keep_files)} files (essential for system)")
    print(f"🗑️ SAFE TO DELETE: {len(delete_files)} files")
    print(f"❓ REVIEW: {len(review_files)} files")
    
    return {
        'keep': keep_files,
        'delete': delete_files, 
        'review': review_files,
        'categories': categories
    }

if __name__ == "__main__":
    results = main()
