#!/usr/bin/env python3
"""
Cleanup utility for temporary files
Removes old temporary files that may have been left behind
"""

import os
import time
import glob
from pathlib import Path

def cleanup_temp_files(temp_dir="temp", max_age_hours=24):
    """
    Clean up temporary files older than max_age_hours
    
    Args:
        temp_dir: Directory containing temporary files
        max_age_hours: Maximum age of files to keep (in hours)
    """
    if not os.path.exists(temp_dir):
        print(f"Temp directory {temp_dir} does not exist")
        return
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    # Find all temp files
    temp_pattern = os.path.join(temp_dir, "temp_*")
    temp_files = glob.glob(temp_pattern)
    
    cleaned_count = 0
    failed_count = 0
    
    print(f"Scanning {temp_dir} for temporary files...")
    print(f"Will remove files older than {max_age_hours} hours")
    
    for file_path in temp_files:
        try:
            # Get file modification time
            file_mtime = os.path.getmtime(file_path)
            file_age = current_time - file_mtime
            
            if file_age > max_age_seconds:
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                    print(f"✓ Removed: {os.path.basename(file_path)} (age: {file_age/3600:.1f}h)")
                except PermissionError:
                    print(f"⚠️  File locked: {os.path.basename(file_path)}")
                    failed_count += 1
                except Exception as e:
                    print(f"✗ Error removing {os.path.basename(file_path)}: {e}")
                    failed_count += 1
            else:
                print(f"  Keeping: {os.path.basename(file_path)} (age: {file_age/3600:.1f}h)")
                
        except Exception as e:
            print(f"✗ Error checking {file_path}: {e}")
            failed_count += 1
    
    print(f"\nCleanup completed:")
    print(f"  Files removed: {cleaned_count}")
    print(f"  Files failed: {failed_count}")
    print(f"  Files kept: {len(temp_files) - cleaned_count - failed_count}")

def force_cleanup_all(temp_dir="temp"):
    """
    Force cleanup all temporary files regardless of age
    Use with caution!
    """
    if not os.path.exists(temp_dir):
        print(f"Temp directory {temp_dir} does not exist")
        return
    
    temp_pattern = os.path.join(temp_dir, "temp_*")
    temp_files = glob.glob(temp_pattern)
    
    if not temp_files:
        print("No temporary files found")
        return
    
    print(f"Found {len(temp_files)} temporary files")
    response = input("Are you sure you want to delete ALL temporary files? (y/N): ")
    
    if response.lower() != 'y':
        print("Cleanup cancelled")
        return
    
    cleaned_count = 0
    failed_count = 0
    
    for file_path in temp_files:
        try:
            os.remove(file_path)
            cleaned_count += 1
            print(f"✓ Removed: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"✗ Error removing {os.path.basename(file_path)}: {e}")
            failed_count += 1
    
    print(f"\nForce cleanup completed:")
    print(f"  Files removed: {cleaned_count}")
    print(f"  Files failed: {failed_count}")

def show_temp_files_info(temp_dir="temp"):
    """Show information about temporary files"""
    if not os.path.exists(temp_dir):
        print(f"Temp directory {temp_dir} does not exist")
        return
    
    temp_pattern = os.path.join(temp_dir, "temp_*")
    temp_files = glob.glob(temp_pattern)
    
    if not temp_files:
        print("No temporary files found")
        return
    
    current_time = time.time()
    total_size = 0
    
    print(f"Found {len(temp_files)} temporary files:")
    print("-" * 80)
    
    for file_path in temp_files:
        try:
            file_size = os.path.getsize(file_path)
            file_mtime = os.path.getmtime(file_path)
            file_age = current_time - file_mtime
            
            total_size += file_size
            
            print(f"{os.path.basename(file_path):<50} {file_size:>10} bytes  {file_age/3600:>6.1f}h old")
        except Exception as e:
            print(f"{os.path.basename(file_path):<50} ERROR: {e}")
    
    print("-" * 80)
    print(f"Total size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "clean":
            max_age = 24
            if len(sys.argv) > 2:
                try:
                    max_age = int(sys.argv[2])
                except ValueError:
                    print("Invalid age parameter. Using default 24 hours.")
            cleanup_temp_files(max_age_hours=max_age)
            
        elif command == "force":
            force_cleanup_all()
            
        elif command == "info":
            show_temp_files_info()
            
        else:
            print("Unknown command. Use: clean [hours], force, or info")
    else:
        print("Usage: python cleanup_temp_files.py [command]")
        print("Commands:")
        print("  clean [hours]  - Clean files older than hours (default: 24)")
        print("  force          - Force delete all temp files")
        print("  info           - Show info about temp files")
        print("\nExample: python cleanup_temp_files.py clean 12") 