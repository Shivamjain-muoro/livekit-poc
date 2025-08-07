"""
Quick Test of Fixed Tools
"""

from fixed_interview_tools import start_interview_session
import json

print("Testing start_interview_session...")

try:
    result = start_interview_session(
        candidate_name="Test Candidate",
        position="Software Engineer"
    )
    print("✅ Function call successful!")
    print(f"Result: {result[:200]}...")  # Show first 200 chars
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exc()
