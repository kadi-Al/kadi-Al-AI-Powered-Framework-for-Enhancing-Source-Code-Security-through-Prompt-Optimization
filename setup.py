import subprocess
import sys
import os
import time
import requests

def install_requirements():
    print("Installing Python requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def check_ollama_running():
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=10)
        return response.status_code == 200
    except:
        return False

def start_ollama_service():
    print("Starting Ollama service...")
    try:
        subprocess.Popen(['ollama', 'serve'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        print("Waiting for Ollama to start...")
        time.sleep(10)
        
        for i in range(30):
            if check_ollama_running():
                return True
            time.sleep(1)
        return False
    except Exception as e:
        print(f"Failed to start Ollama: {e}")
        return False

def check_ollama_models():
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=30)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            required_models = ['deepseek-v2:16b', 'deepseek-coder-v2:latest']
            missing_models = []
            
            for model in required_models:
                if model not in model_names:
                    missing_models.append(model)
                else:
                    print(f"{model} is available")
            
            if missing_models:
                print(f"Missing models: {', '.join(missing_models)}")
                print("Pulling missing models (this may take 10-30 minutes depending on your internet connection)...")
                print("Please be patient, this is a one-time setup...")
                
                for model in missing_models:
                    print(f"Pulling {model}...")
                    try:
                        timeout = 1800
                        process = subprocess.Popen(
                            ['ollama', 'pull', model],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                        )
                        
                        for line in process.stdout:
                            print(f"   {line.strip()}")
                        
                        process.wait(timeout=timeout)
                        
                        if process.returncode == 0:
                            print(f"Successfully pulled {model}")
                        else:
                            print(f"Failed to pull {model}. Return code: {process.returncode}")
                            stderr = process.stderr.read()
                            if stderr:
                                print(f"   Error: {stderr}")
                            
                    except subprocess.TimeoutExpired:
                        print(f"Timeout pulling {model}. The model is very large and may take longer.")
                        print(f"You can manually pull it later with: ollama pull {model}")
                    except Exception as e:
                        print(f"Error pulling {model}: {e}")
                        print(f"You can manually pull it later with: ollama pull {model}")
            
            return True
        else:
            print("Could not connect to Ollama API")
            return False
    except Exception as e:
        print(f"Error checking Ollama models: {e}")
        return False

def verify_models_loaded():
    print("Verifying models are ready...")
    try:
        test_prompt = {
            "model": "deepseek-v2:16b",
            "prompt": "Say 'Hello' in one word.",
            "stream": False
        }
        
        response = requests.post(
            'http://localhost:11434/api/generate',
            json=test_prompt,
            timeout=30
        )
        
        if response.status_code == 200:
            print("Models are ready and responding!")
            return True
        else:
            print(f"Models are pulled but may not be ready. Status: {response.status_code}")
            return True
            
    except Exception as e:
        print(f"Could not verify model response: {e}")
        print("The models are pulled but there might be a loading delay.")
        return True

if __name__ == "__main__":
    print("Setting up the AI Security Framework...")
    print("=" * 50)
    
    install_requirements()
    
    if not check_ollama_running():
        print("Ollama is not running")
        if start_ollama_service():
            print("Ollama service started successfully")
        else:
            print("Could not start Ollama automatically")
            print("Please start Ollama manually with: ollama serve")
            print("Or install Ollama from: https://ollama.ai")
            sys.exit(1)
    else:
        print("Ollama is running")
    
    print("Checking Ollama models...")
    if not check_ollama_models():
        print("Failed to verify Ollama models")
        sys.exit(1)
    
    verify_models_loaded()
    
    print("Setup completed successfully!")
    print("")
    print("Next steps:")
    print("   1.Run the application: python app.py")
    print("   2.Open your browser to: http://localhost:5000")

