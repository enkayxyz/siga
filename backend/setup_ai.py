import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq
from openai import OpenAI

# Load existing env
ENV_FILE = "backend/.env"
load_dotenv(ENV_FILE)

GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def save_env(key, value):
    # Read current file
    lines = []
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            lines = f.readlines()

    # Update or Append
    updated = False
    new_lines = []
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            updated = True
        else:
            new_lines.append(line)
    
    if not updated:
        new_lines.append(f"{key}={value}\n")

    with open(ENV_FILE, "w") as f:
        f.writelines(new_lines)
    
    # Update current process env so subsequent calls use it
    os.environ[key] = value

def mask_key(key):
    if not key or len(key) < 5:
        return ""
    return f"...{key[-4:]}"

def get_input(prompt, default=None):
    if default:
        user_input = input(f"{prompt} [{default}]: ")
        return user_input.strip() or default
    else:
        return input(f"{prompt}: ").strip()

def setup_openai():
    print(f"\n{BLUE}--- OpenAI Setup ---{RESET}")
    current_key = os.environ.get("OPENAI_API_KEY", "")
    key = get_input("Enter OpenAI API Key", mask_key(current_key))
    
    if key != mask_key(current_key):
        save_env("OPENAI_API_KEY", key)
    else:
        key = current_key

    if not key:
        print("Skipping OpenAI configuration.")
        return

    # Fetch Models
    try:
        client = OpenAI(api_key=key)
        print("Fetching available models...")
        models = [m.id for m in client.models.list()]
        models.sort()
        
        # Filter for chat models roughly
        chat_models = [m for m in models if "gpt" in m]
        
        print(f"Available Models: {', '.join(chat_models[:5])}...")
        current_model = os.environ.get("OPENAI_MODEL", "gpt-4o")
        
        print("Select a model or type manually:")
        for i, m in enumerate(chat_models[:10]):
            print(f"{i+1}. {m}")
        
        choice = get_input("Enter Model Name or Number", current_model)
        
        if choice.isdigit() and 1 <= int(choice) <= len(chat_models[:10]):
            model = chat_models[int(choice)-1]
        else:
            model = choice
            
        save_env("OPENAI_MODEL", model)
        print(f"{GREEN}OpenAI Configured.{RESET}")
        
    except Exception as e:
        print(f"{YELLOW}Could not fetch models: {e}{RESET}")
        current_model = os.environ.get("OPENAI_MODEL", "gpt-4o")
        model = get_input("Enter OpenAI Model manually", current_model)
        save_env("OPENAI_MODEL", model)

def setup_groq():
    print(f"\n{BLUE}--- Groq Setup ---{RESET}")
    current_key = os.environ.get("GROQ_API_KEY", "")
    key = get_input("Enter Groq API Key", mask_key(current_key))
    
    if key != mask_key(current_key):
        save_env("GROQ_API_KEY", key)
    else:
        key = current_key

    if not key:
        print("Skipping Groq configuration.")
        return

    try:
        client = Groq(api_key=key)
        print("Fetching available models...")
        models = [m.id for m in client.models.list().data]
        models.sort()
        
        print("Select a model or type manually:")
        for i, m in enumerate(models):
            print(f"{i+1}. {m}")
            
        current_model = os.environ.get("GROQ_MODEL", "mixtral-8x7b-32768")
        choice = get_input("Enter Model Name or Number", current_model)
        
        if choice.isdigit() and 1 <= int(choice) <= len(models):
            model = models[int(choice)-1]
        else:
            model = choice
            
        save_env("GROQ_MODEL", model)
        print(f"{GREEN}Groq Configured.{RESET}")

    except Exception as e:
        print(f"{YELLOW}Could not fetch models: {e}{RESET}")
        current_model = os.environ.get("GROQ_MODEL", "mixtral-8x7b-32768")
        model = get_input("Enter Groq Model manually", current_model)
        save_env("GROQ_MODEL", model)

def setup_gemini():
    print(f"\n{BLUE}--- Gemini Setup ---{RESET}")
    current_key = os.environ.get("GEMINI_API_KEY", "")
    key = get_input("Enter Gemini API Key", mask_key(current_key))
    
    if key != mask_key(current_key):
        save_env("GEMINI_API_KEY", key)
    else:
        key = current_key

    if not key:
        print("Skipping Gemini configuration.")
        return

    try:
        genai.configure(api_key=key)
        print("Fetching available models...")
        models = [m.name.replace("models/", "") for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        models.sort()
        
        print("Select a model or type manually:")
        for i, m in enumerate(models):
            print(f"{i+1}. {m}")
            
        current_model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        choice = get_input("Enter Model Name or Number", current_model)
        
        if choice.isdigit() and 1 <= int(choice) <= len(models):
            model = models[int(choice)-1]
        else:
            model = choice
            
        save_env("GEMINI_MODEL", model)
        print(f"{GREEN}Gemini Configured.{RESET}")

    except Exception as e:
        print(f"{YELLOW}Could not fetch models: {e}{RESET}")
        current_model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        model = get_input("Enter Gemini Model manually", current_model)
        save_env("GEMINI_MODEL", model)

def setup_tavily():
    print(f"\n{BLUE}--- Tavily Setup ---{RESET}")
    current_key = os.environ.get("TAVILY_API_KEY", "")
    key = get_input("Enter Tavily API Key", mask_key(current_key))
    
    if key != mask_key(current_key):
        save_env("TAVILY_API_KEY", key)
    
    print(f"{GREEN}Tavily Configured.{RESET}")

def select_provider():
    print(f"\n{BLUE}--- Default Provider ---{RESET}")
    current = os.environ.get("LLM_PROVIDER", "openai")
    print("1. openai")
    print("2. groq")
    print("3. gemini")
    
    choice = get_input("Select Default Provider", current)
    
    if choice == "1": provider = "openai"
    elif choice == "2": provider = "groq"
    elif choice == "3": provider = "gemini"
    else: provider = choice
    
    save_env("LLM_PROVIDER", provider)
    print(f"{GREEN}Default Provider set to: {provider}{RESET}")

def main():
    print("Interactive AI Setup")
    setup_openai()
    setup_groq()
    setup_gemini()
    setup_tavily()
    select_provider()
    print(f"\n{GREEN}Configuration saved to {ENV_FILE}{RESET}")

if __name__ == "__main__":
    main()
