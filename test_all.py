import subprocess
import sys

def run_tests():
    """Runs all tests using pytest."""
    print("🚀 Running all tests...")
    result = subprocess.run([sys.executable, "-m", "pytest", "backend/tests"], capture_output=False)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed.")
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    run_tests()
