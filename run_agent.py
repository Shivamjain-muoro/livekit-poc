#!/usr/bin/env python3
"""
Simple LiveKit Agent Launcher for Live Interviews
=================================================
This script runs a LiveKit agent that can join interview rooms and conduct interviews.
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()

async def main():
    """Run the interview agent"""
    
    # Check if LiveKit credentials are configured
    if not os.getenv("LIVEKIT_API_KEY") or not os.getenv("LIVEKIT_API_SECRET"):
        print("❌ LiveKit credentials not configured!")
        print("Please set LIVEKIT_API_KEY and LIVEKIT_API_SECRET in your .env file")
        return
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Google API key not configured!")
        print("Please set GOOGLE_API_KEY in your .env file")
        return
        
    print("🤖 Starting AI Interview Agent...")
    print(f"🔑 LiveKit URL: {os.getenv('LIVEKIT_URL', 'wss://testpoc-mys8x433.livekit.cloud')}")
    print("🎯 Agent will join interview rooms automatically when participants connect")
    print("📞 Listening for interview sessions...")
    
    try:
        from enhanced_agent import InterviewAgent
        
        # Create and run the agent
        agent = InterviewAgent()
        await agent.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Agent stopped by user")
    except Exception as e:
        print(f"❌ Error running agent: {e}")
        logging.exception("Agent error")

if __name__ == "__main__":
    asyncio.run(main())
