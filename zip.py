import zipfile

def check_my_zip(zip_name):
    print(f"🧐 Scanning {zip_name} for sensitive files...")
    
    with zipfile.ZipFile(zip_name, 'r') as z:
        files = z.namelist()
        
        # Look for forbidden files
        forbidden = [f for f in files if '.env' in f or 'venv/' in f]
        
        if forbidden:
            print("❌ SECURITY ALERT! The following should NOT be in there:")
            for item in forbidden:
                print(f"  - {item}")
        else:
            print("✅ Clean! No .env or venv detected.")
            
        print(f"\n📦 Total files in zip: {len(files)}")
        # Optional: Print the first 10 files to verify structure
        print("📝 Top 5 files in root:")
        for f in files[:5]:
            print(f"  - {f}")

if __name__ == "__main__":
    # Ensure this matches your actual zip filename
    check_my_zip("procurebot_final.zip")