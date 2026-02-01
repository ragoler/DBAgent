import os
import sys
import argparse

# Add the project root to the Python path
# This ensures that absolute imports like 'from backend.core...' work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Database Agentic System.")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the web server on.")
    args = parser.parse_args()

    try:
        from backend.main import app
        import uvicorn
        
        print("\n🚀 Starting Database Agentic System...")
        print(f"📍 Backend API: http://localhost:{args.port}/health")
        print(f"🌐 Frontend UI:  http://localhost:{args.port}")
        print("-" * 40)
        
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    except ImportError as e:
        print(f"❌ Error: Could not import application modules. {e}")
        print("💡 Make sure you have activated the virtual environment and installed dependencies:")
        print("   source .venv/bin/activate")
        print("   pip install -r backend/requirements.txt")
        sys.exit(1)
