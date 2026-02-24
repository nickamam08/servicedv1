import os

for root, dirs, files in os.walk("."):
    if "legacy_v1" in root or ".git" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if "Message" in line and "import" in line:
                            # Print the line if it imports Message exactly (not ChatMessage)
                            # Regex to find exactly 'Message'
                            import re
                            if re.search(r"\bMessage\b", line):
                                print(f"{path}:{i}: {line.strip()}")
            except Exception:
                pass
