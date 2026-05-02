import zipfile
import os

def build_lambda():
    zip_name = "procurebot_final.zip"
    dist_folder = "lambda_dist"
    # The core files that MUST be at the top level
    core_files = [
        "supervisor.py", 
        "sourcer_agent.py", 
        "risk_analyst.py", 
        "config_manager.py", 
        "groq_llm.py"
    ]

    print(f"🚀 Building {zip_name}...")

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as z:
        # 1. Add the core files first
        for f in core_files:
            file_path = os.path.join(dist_folder, f)
            if os.path.exists(file_path):
                z.write(file_path, f) # 'f' as arcname ensures it's at the root
                print(f" ✅ Added core: {f}")
            else:
                print(f" ❌ Missing file: {file_path}")

        # 2. Add everything else (libraries)
        print(" 📦 Packing libraries (this may take a moment)...")
        for root, dirs, files in os.walk(dist_folder):
            for file in files:
                if file not in core_files:
                    full_path = os.path.join(root, file)
                    # Create the path inside the zip (relative to dist_folder)
                    rel_path = os.path.relpath(full_path, dist_folder)
                    z.write(full_path, rel_path)

    print(f"\n✨ Success! {zip_name} is ready for AWS.")

if __name__ == "__main__":
    build_lambda()