import os
import sys

# Add the project root to the Python path
# This ensures that absolute imports like 'from backend.core...' work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        from backend.main import app
        import uvicorn
        
        print("\n🚀 Starting Database Agentic System...")
        print("📍 Backend API: http://localhost:8000/health")
        print("🌐 Frontend UI:  http://localhost:8000")
        print("-" * 40)
        
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError as e:
        print(f"❌ Error: Could not import application modules. {e}")
        print("💡 Make sure you have activated the virtual environment and installed dependencies:")
        print("   source .venv/bin/activate")
        print("   pip install -r backend/requirements.txt")
        sys.exit(1)
