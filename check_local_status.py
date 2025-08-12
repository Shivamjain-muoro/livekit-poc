"""
Quick Local System Status Checker
Check if all components are running properly
"""

import requests
import subprocess
import sqlite3
import os
from datetime import datetime

def check_livekit_server():
    """Check if LiveKit server is running"""
    try:
        # Try to connect to LiveKit server
        response = requests.get('http://localhost:7880', timeout=3)
        return True, "Online"
    except requests.exceptions.RequestException:
        try:
            # Check if Docker container is running
            result = subprocess.run(['docker', 'ps', '--filter', 'name=livekit-local', '--format', '{{.Status}}'], 
                                  capture_output=True, text=True, timeout=5)
            if result.stdout.strip():
                return False, "Container running but not responding"
            else:
                return False, "Container not running"
        except:
            return False, "Docker not available"

def check_web_server():
    """Check if web server is running"""
    try:
        response = requests.get('http://localhost:8080', timeout=3)
        return True, "Online"
    except requests.exceptions.RequestException:
        return False, "Not running"

def check_database():
    """Check database status"""
    try:
        db_path = os.path.join("database", "interview_evaluations.db")
        if not os.path.exists(db_path):
            return False, "Database file not found"
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM interview_sessions")
            sessions = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM interview_exchanges")
            exchanges = cursor.fetchone()[0]
            
            return True, f"{sessions} sessions, {exchanges} exchanges"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_environment():
    """Check environment configuration"""
    env_path = os.path.join("config", ".env")
    if not os.path.exists(env_path):
        return False, "Environment file not found"
    
    from dotenv import load_dotenv
    load_dotenv(env_path)
    
    livekit_url = os.getenv('LIVEKIT_URL')
    api_key = os.getenv('LIVEKIT_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    if not all([livekit_url, api_key, google_key]):
        return False, "Missing required environment variables"
    
    if 'localhost' in livekit_url:
        return True, "Local configuration active"
    else:
        return True, "Cloud configuration active"

def main():
    print("🏠 LOCAL AI INTERVIEW SYSTEM - STATUS CHECK")
    print("=" * 60)
    print(f"📅 Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check all components
    checks = [
        ("🔧 Environment Config", check_environment),
        ("🐳 LiveKit Server", check_livekit_server),
        ("🌐 Web Server", check_web_server),
        ("💾 Database", check_database),
    ]
    
    all_good = True
    
    for component, check_func in checks:
        try:
            status, message = check_func()
            if status:
                print(f"✅ {component}: {message}")
            else:
                print(f"❌ {component}: {message}")
                all_good = False
        except Exception as e:
            print(f"❌ {component}: Error - {str(e)}")
            all_good = False
    
    print("=" * 60)
    
    if all_good:
        print("🎉 ALL SYSTEMS GO! Ready for interviews.")
    else:
        print("⚠️  ISSUES DETECTED. Check the items above.")
        print()
        print("🛠️  TROUBLESHOOTING STEPS:")
        print("   1. Start system: start_local_system.bat")
        print("   2. Check Docker: docker ps")
        print("   3. Check ports: netstat -an | findstr :7880")
        print("   4. Check logs: docker logs livekit-local")
    
    print("=" * 60)
    
    # Show quick commands
    print("📋 QUICK COMMANDS:")
    print("   🚀 Start system: start_local_system.bat")
    print("   🛑 Stop system:  stop_local_system.bat")
    print("   🔍 Check logs:   docker logs livekit-local")
    print("   🎯 Generate URL: python local_token_generator.py")
    print()

if __name__ == "__main__":
    main()
