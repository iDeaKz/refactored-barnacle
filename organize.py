import os
import shutil
import hashlib

# Define the base directory
base_dir = r"D:\portfolio\precision"

# Define the target structure and file mappings
file_mappings = {
    "#!binbash.txt": "scripts/deploy.sh",
    ".gitignore": ".gitignore",
    "appapi__init__.py": "app/api/__init__.py",
    "appapiroutes.py": "app/api/routes.py",
    "appconfig__init__.py": "app/config/__init__.py",
    "appconfigconfig.yaml": "app/config/config.yaml",
    "appdatacollector.py": "app/data/collector.py",
    "appdataprocessor.py": "app/data/processor.py",
    "appguimain.py": "app/gui/main.py",
    "appguiui_main.py": "app/gui/ui_main.py",
    "appmodelspredictor.py": "app/models/predictor.py",
    "apputilslogger.py": "app/utils/logger.py",
    "apputilsmonetization.py": "app/utils/monetization.py",
    "Dockerfile.txt": "Dockerfile",
    "pre-commit-config.yaml": "pre-commit-config.yaml",
    "pyproject.toml": "pyproject.toml",
    "requirements.txt": "requirements.txt",
    "ryptocurrency Precision Price Pr.txt": "README.md",
    "testsconfig_test.yaml": "tests/config_test.yaml",
    "testsconftest.py": "tests/conftest.py",
    "teststest_api.py": "tests/test_api.py",
    "teststest_collector.py": "tests/test_collector.py",
    "teststest_predictor.py": "tests/test_predictor.py",
    "teststest_processor.py": "tests/test_processor.py",
}

# Function to calculate the file hash for verification
def calculate_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

# Function to organize files, rename, and verify
def organize_files(base_dir, file_mappings):
    for src_file, dest_path in file_mappings.items():
        src_path = os.path.join(base_dir, src_file)
        dest_path = os.path.join(base_dir, dest_path)
        
        # Create target directories if they don't exist
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        try:
            # Verify source file exists
            if not os.path.exists(src_path):
                print(f"File not found: {src_path}")
                continue
            
            # Calculate source file hash before moving
            original_hash = calculate_file_hash(src_path)
            
            # Move and rename the file
            shutil.move(src_path, dest_path)
            print(f"Moved: {src_path} -> {dest_path}")
            
            # Verify the destination file hash matches the source file hash
            if os.path.exists(dest_path):
                new_hash = calculate_file_hash(dest_path)
                if original_hash == new_hash:
                    print(f"Verified: {dest_path}")
                else:
                    print(f"Hash mismatch for: {dest_path}")
            else:
                print(f"Destination file missing: {dest_path}")
        
        except Exception as e:
            print(f"Error moving {src_path}: {e}")

# Run the function
organize_files(base_dir, file_mappings)
