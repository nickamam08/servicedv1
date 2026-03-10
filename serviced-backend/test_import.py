import sys
import os
sys.path.append(os.getcwd())

file_path = os.path.join(os.getcwd(), "app", "api", "v1", "routes", "services.py")
print(f"Reading file at: {file_path}")
try:
    with open(file_path, 'r') as f:
        print("--- DISK CONTENT START ---")
        print(f.read())
        print("--- DISK CONTENT END ---")
except Exception as e:
    print(f"Error reading file: {e}")

print("Attempting import...")
try:
    import app.api.v1.routes.services
    print("Import successful")
except Exception as e:
    import traceback
    traceback.print_exc()
