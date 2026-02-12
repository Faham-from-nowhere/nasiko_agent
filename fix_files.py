import os

# Target directory
target_dir = r"D:\the-codex-project" #change to your project path

print(f"🧹 Cleaning BOM (U+FEFF) from files in {target_dir}...")

for root, dirs, files in os.walk(target_dir):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            
            # Read with 'utf-8-sig' (automatically handles/removes BOM)
            try:
                with open(path, "r", encoding="utf-8-sig") as f:
                    content = f.read()
                
                # Write back as standard 'utf-8' (No BOM)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                    
                print(f"✅ Cleaned: {file}")
            except Exception as e:
                print(f"❌ Error {file}: {e}")

print("✨ All files are now clean Python scripts.")