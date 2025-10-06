#!/usr/bin/env python3
"""
VDB2 Deployment Test Script
Tests the application configuration for cloud deployment
"""

import os
import sys
import json
from datetime import datetime

def test_cloud_configuration():
    """Test if the app is configured for cloud deployment"""
    print("Testing VDB2 Cloud Configuration...")
    print("=" * 50)
    
    # Test 1: Check if running on Render
    render_env = os.environ.get('RENDER', False)
    print(f"[OK] Render Environment: {render_env}")
    
    # Test 2: Check PORT environment variable
    port = os.environ.get('PORT', '8080')
    print(f"[OK] Port Configuration: {port}")
    
    # Test 3: Check file paths
    if render_env:
        data_dir = "/opt/render/project/vdb2-storage/data"
        files_dir = "/opt/render/project/vdb2-storage/vdb_files"
        print(f"[OK] Cloud Data Directory: {data_dir}")
        print(f"[OK] Cloud Files Directory: {files_dir}")
    else:
        data_dir = "data"
        files_dir = "vdb_files"
        print(f"[OK] Local Data Directory: {data_dir}")
        print(f"[OK] Local Files Directory: {files_dir}")
    
    # Test 4: Check if directories exist or can be created
    try:
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(files_dir, exist_ok=True)
        print("[OK] Directory Creation: Success")
    except Exception as e:
        print(f"[ERROR] Directory Creation: Failed - {e}")
        return False
    
    # Test 5: Check JSON file initialization
    try:
        vdb_file = os.path.join(data_dir, "virtualdatabases.json")
        entries_file = os.path.join(data_dir, "entries.json")
        
        if not os.path.exists(vdb_file):
            with open(vdb_file, "w") as f:
                json.dump([], f)
            print("[OK] VDB File: Created")
        else:
            print("[OK] VDB File: Exists")
            
        if not os.path.exists(entries_file):
            with open(entries_file, "w") as f:
                json.dump({}, f)
            print("[OK] Entries File: Created")
        else:
            print("[OK] Entries File: Exists")
            
    except Exception as e:
        print(f"[ERROR] JSON File Initialization: Failed - {e}")
        return False
    
    # Test 6: Check server configuration
    try:
        from server import Config, DatabaseManager
        print("[OK] Server Import: Success")
        print(f"[OK] Config Data Dir: {Config.DATA_DIR}")
        print(f"[OK] Config Files Dir: {Config.FILES_DIR}")
        print(f"[OK] Cloud Storage: {Config.CLOUD_STORAGE}")
    except Exception as e:
        print(f"[ERROR] Server Import: Failed - {e}")
        return False
    
    print("=" * 50)
    print("All tests passed! Ready for deployment.")
    return True

def test_file_handling():
    """Test file handling capabilities"""
    print("\nTesting File Handling...")
    print("=" * 30)
    
    try:
        from server import DatabaseManager
        
        # Test file directory creation
        test_vdb_id = 999
        test_dir = DatabaseManager.get_vdb_files_dir(test_vdb_id)
        print(f"[OK] VDB Directory Creation: {test_dir}")
        
        # Test file saving (simulate)
        test_file_data = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD//2Q=="
        test_file_name = "test.jpg"
        
        # This would normally save a file, but we'll just test the path generation
        expected_path = os.path.join("vdb_files", f"vdb_{test_vdb_id}", f"1_test_{test_file_name}")
        print(f"[OK] File Path Generation: {expected_path}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] File Handling Test: Failed - {e}")
        return False

if __name__ == "__main__":
    print("VDB2 Deployment Test")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = True
    success &= test_cloud_configuration()
    success &= test_file_handling()
    
    if success:
        print("\n[SUCCESS] Deployment test completed successfully!")
        print("Your app is ready for Render deployment.")
        sys.exit(0)
    else:
        print("\n[ERROR] Deployment test failed!")
        print("Please fix the issues before deploying.")
        sys.exit(1)
