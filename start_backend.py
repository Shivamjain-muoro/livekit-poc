"""
Start Voice Interview Backend
============================
Simple script to start the voice interview backend server.
"""

import subprocess
import sys
import os
import time

def start_backend():
    """Start the voice interview backend"""
    
    print("🚀 Starting Voice Interview Backend...")
    print("=" * 50)
    
    # Get the correct Python path
    python_path = r"C:\Users\ADMIN\projects\livekit-poc\venv\Scripts\python.exe"
    backend_file = "realtime_voice_backend.py"
    
    # Check if files exist
    if not os.path.exists(python_path):
        print(f"❌ Python not found at: {python_path}")
        return False
    
    if not os.path.exists(backend_file):
        print(f"❌ Backend file not found: {backend_file}")
        return False
    
    try:
        print(f"🐍 Using Python: {python_path}")
        print(f"📁 Backend file: {backend_file}")
        print()
        print("🌐 Backend will start on: http://localhost:8003")
        print("🎙️ Voice demo will be at: http://localhost:8003/voice-demo")
        print()
        print("Starting server... (Ctrl+C to stop)")
        print("-" * 50)
        
        # Start the backend
        result = subprocess.run([
            python_path, 
            backend_file
        ])
        
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False

if __name__ == "__main__":
    success = start_backend()
    if not success:
        print("\n💡 Try starting manually:")
        print("   C:/Users/ADMIN/projects/livekit-poc/venv/Scripts/python.exe realtime_voice_backend.py")
    
    input("\nPress Enter to exit...")
