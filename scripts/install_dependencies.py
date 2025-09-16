#!/usr/bin/env python3
"""
Installation script for multi-format file processing dependencies
"""

import subprocess
import sys
import platform
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Installing {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {description}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_tesseract():
    """Check if Tesseract is installed"""
    try:
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Tesseract is already installed")
            return True
    except FileNotFoundError:
        pass
    return False

def install_tesseract():
    """Install Tesseract OCR based on the operating system"""
    system = platform.system().lower()
    
    if system == "windows":
        print("For Windows, please install Tesseract manually:")
        print("1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install and add to PATH environment variable")
        print("3. Restart your terminal/IDE")
        return False
    
    elif system == "linux":
        # Try different package managers
        if run_command("which apt-get", "checking apt-get"):
            return run_command("sudo apt-get update && sudo apt-get install -y tesseract-ocr", "Tesseract OCR")
        elif run_command("which yum", "checking yum"):
            return run_command("sudo yum install -y tesseract", "Tesseract OCR")
        elif run_command("which dnf", "checking dnf"):
            return run_command("sudo dnf install -y tesseract", "Tesseract OCR")
        else:
            print("Could not find a supported package manager. Please install Tesseract manually.")
            return False
    
    elif system == "darwin":  # macOS
        return run_command("brew install tesseract", "Tesseract OCR")
    
    else:
        print(f"Unsupported operating system: {system}")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    
    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip", "pip")
    
    # Install requirements
    requirements_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "requirements.txt")
    if os.path.exists(requirements_file):
        return run_command(f"{sys.executable} -m pip install -r {requirements_file}", "Python dependencies")
    else:
        print("requirements.txt not found. Installing core dependencies...")
        core_deps = [
            "fastapi", "uvicorn", "pydantic", "requests", "python-dotenv",
            "pandas", "openpyxl", "python-pptx", "Pillow", "pytesseract",
            "PyPDF2", "python-docx", "loguru"
        ]
        for dep in core_deps:
            run_command(f"{sys.executable} -m pip install {dep}", dep)
        return True

def main():
    """Main installation function"""
    print("Setting up multi-format file processing dependencies...")
    print("=" * 60)
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("Failed to install Python dependencies")
        return False
    
    print("\n" + "=" * 60)
    
    # Check and install Tesseract
    if not check_tesseract():
        print("\nTesseract OCR is required for image processing...")
        if not install_tesseract():
            print("\n⚠️  Warning: Tesseract installation failed.")
            print("Image processing (OCR) will not work without Tesseract.")
            print("You can still process other file types (PDF, DOCX, PPTX, XLSX, ZIP, BIN).")
    
    print("\n" + "=" * 60)
    print("Installation completed!")
    print("\nTo test the installation, run:")
    print("python scripts/test_file_processing.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 