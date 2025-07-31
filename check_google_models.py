"""
Check available Google models and find alternatives
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def check_available_models():
    """Check what Google models are actually available"""
    
    print("🔍 Checking Available Google Models")
    print("=" * 50)
    
    # Configure API
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    
    try:
        models = list(genai.list_models())
        print(f"✅ Found {len(models)} total models")
        
        # Categorize models
        text_models = []
        gemini_models = []
        other_models = []
        
        for model in models:
            model_name = model.name.lower()
            if 'gemini' in model_name:
                gemini_models.append(model.name)
            elif 'text' in model_name or 'chat' in model_name:
                text_models.append(model.name)
            else:
                other_models.append(model.name)
        
        print(f"\n📝 Gemini Models ({len(gemini_models)}):")
        for model in gemini_models[:5]:  # Show first 5
            print(f"   - {model}")
        if len(gemini_models) > 5:
            print(f"   ... and {len(gemini_models) - 5} more")
        
        print(f"\n💬 Text/Chat Models ({len(text_models)}):")
        for model in text_models[:5]:  # Show first 5
            print(f"   - {model}")
        if len(text_models) > 5:
            print(f"   ... and {len(text_models) - 5} more")
        
        print(f"\n🔧 Other Models ({len(other_models)}):")
        for model in other_models[:5]:  # Show first 5
            print(f"   - {model}")
        if len(other_models) > 5:
            print(f"   ... and {len(other_models) - 5} more")
        
        # Look for realtime specifically
        realtime_models = [m for m in models if 'realtime' in m.name.lower()]
        if realtime_models:
            print(f"\n🎤 Realtime Models ({len(realtime_models)}):")
            for model in realtime_models:
                print(f"   - {model.name}")
        else:
            print(f"\n❌ No realtime models found")
            print("💡 Suggestion: Use OpenAI for voice or Gemini for text-only")
        
    except Exception as e:
        print(f"❌ Error listing models: {e}")

if __name__ == "__main__":
    check_available_models()
