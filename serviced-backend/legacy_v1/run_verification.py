import subprocess
import time
import sys
import os

def run_tests():
    # Start Server
    print("Starting server...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"],
        cwd=os.getcwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='ascii',
        errors='ignore'
    )
    
    # Wait for server to start
    time.sleep(5)
    
    # Run Tests
    print("Running tests...")
    test_result = subprocess.run(
        [sys.executable, "test_profile_backend.py"],
        capture_output=True,
        text=True,
        encoding='ascii',
        errors='ignore'
    )
    
    print("Test Output:")
    print(test_result.stdout)
    print(test_result.stderr)
    
    # Kill Server
    print("Stopping server...")
    server_process.terminate()
    try:
        outs, errs = server_process.communicate(timeout=5)
        print("Server Output:")
        print(outs.decode('utf-8', errors='replace') if outs else "")
        print("Server Errors:")
        print(errs.decode('utf-8', errors='replace') if errs else "")
    except Exception as e:
        print(f"Could not read server headers: {e}")
    
    if "ALL TESTS PASSED!" in test_result.stdout:
        print("SUCCESS: Integration tests passed.")
    else:
        print("FAILURE: Integration tests failed.")

if __name__ == "__main__":
    run_tests()
