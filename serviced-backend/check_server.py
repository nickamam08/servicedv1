import traceback
import sys
import os

def check_import(module_name):
    try:
        print(f"Checking {module_name}...")
        mod = __import__(module_name, fromlist=['*'])
        print(f"  - Successfully imported {module_name}")
        return mod
    except ImportError as e:
        print(f"  - ImportError caught while importing {module_name}: {e}")
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"  - Error in {module_name}: {e}")
        traceback.print_exc()
        return None

print("--- EXHAUSTIVE DIAGNOSTIC START ---")
# Check core first
check_import("app.db.base")
check_import("app.models.all_models")
check_import("app.models")

# Check repositories
repo_dir = "app/repositories"
for f in os.listdir(repo_dir):
    if f.endswith(".py") and f != "__init__.py":
        mod_name = f"app.repositories.{f[:-3]}"
        check_import(mod_name)

# Check services
service_dir = "app/services"
for f in os.listdir(service_dir):
    if f.endswith(".py") and f != "__init__.py":
        mod_name = f"app.services.{f[:-3]}"
        check_import(mod_name)

# Check schemas
schema_dir = "app/schemas"
for f in os.listdir(schema_dir):
    if f.endswith(".py") and f != "__init__.py":
        mod_name = f"app.schemas.{f[:-3]}"
        check_import(mod_name)

# Check routes
route_dir = "app/api/v1/routes"
for f in os.listdir(route_dir):
    if f.endswith(".py") and f != "__init__.py":
        mod_name = f"app.api.v1.routes.{f[:-3]}"
        check_import(mod_name)

check_import("app.api.v1.router")
check_import("app.main")
print("--- EXHAUSTIVE DIAGNOSTIC END ---")
