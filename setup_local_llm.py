#!/usr/bin/env python3

import subprocess
import sys
import requests
import time
from loguru import logger

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            logger.warning("Ollama is not installed or not in PATH")
            return False
    except FileNotFoundError:
        logger.warning("Ollama is not installed")
        return False

def install_ollama():
    """Install Ollama"""
    logger.info("Installing Ollama...")
    
    if sys.platform == "win32":
        # Windows installation
        logger.info("Please install Ollama manually from: https://ollama.ai/download")
        logger.info("After installation, run: ollama serve")
        return False
    elif sys.platform == "darwin":
        # macOS installation
        try:
            subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '|', 'sh'], shell=True, check=True)
            logger.info("Ollama installed successfully on macOS")
            return True
        except subprocess.CalledProcessError:
            logger.error("Failed to install Ollama on macOS")
            return False
    else:
        # Linux installation
        try:
            subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '|', 'sh'], shell=True, check=True)
            logger.info("Ollama installed successfully on Linux")
            return True
        except subprocess.CalledProcessError:
            logger.error("Failed to install Ollama on Linux")
            return False

def start_ollama_service():
    """Start Ollama service"""
    logger.info("Starting Ollama service...")
    try:
        # Start Ollama in background
        subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("Ollama service started")
        return True
    except Exception as e:
        logger.error(f"Failed to start Ollama service: {e}")
        return False

def check_ollama_running():
    """Check if Ollama is running"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            logger.info("Ollama is running")
            return True
        else:
            logger.warning("Ollama is not responding properly")
            return False
    except requests.exceptions.ConnectionError:
        logger.warning("Ollama is not running")
        return False
    except Exception as e:
        logger.error(f"Error checking Ollama: {e}")
        return False

def download_model(model_name="llama3.2:3b"):
    """Download a model"""
    logger.info(f"Downloading model: {model_name}")
    try:
        result = subprocess.run(['ollama', 'pull', model_name], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Model {model_name} downloaded successfully")
            return True
        else:
            logger.error(f"Failed to download model: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error downloading model: {e}")
        return False

def test_local_llm():
    """Test local LLM functionality"""
    logger.info("Testing local LLM...")
    try:
        payload = {
            "model": "llama3.2:3b",
            "prompt": "What is 2+2? Answer in one word.",
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 10
            }
        }
        
        response = requests.post('http://localhost:11434/api/generate', json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "").strip()
            logger.info(f"Local LLM test successful. Response: {answer}")
            return True
        else:
            logger.error(f"Local LLM test failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Local LLM test error: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("Setting up local LLM with Ollama...")
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        logger.info("Ollama not found. Attempting to install...")
        if not install_ollama():
            logger.error("Failed to install Ollama. Please install manually from https://ollama.ai")
            return False
    
    # Start Ollama service
    if not check_ollama_running():
        if not start_ollama_service():
            logger.error("Failed to start Ollama service")
            return False
        
        # Wait for service to start
        logger.info("Waiting for Ollama service to start...")
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if check_ollama_running():
                break
        else:
            logger.error("Ollama service failed to start within 30 seconds")
            return False
    
    # Download model
    if not download_model():
        logger.error("Failed to download model")
        return False
    
    # Test local LLM
    if not test_local_llm():
        logger.error("Local LLM test failed")
        return False
    
    logger.info("✅ Local LLM setup completed successfully!")
    logger.info("Your system is now ready to use local LLM for faster responses.")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        logger.error("❌ Local LLM setup failed. You can still use cloud models as fallback.")
    sys.exit(0 if success else 1) 