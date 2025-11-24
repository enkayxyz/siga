import os
import sys
from dotenv import load_dotenv
import asyncio
import google.generativeai as genai
from groq import Groq
# from openai import OpenAI # Assuming openai package is installed

# Load environment variables
# load_dotenv() # Moved to main execution or handled by app

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_status(provider, status, message=""):
    if status == "OK":
        print(f"[{GREEN}OK{RESET}] {provider:<10} : Connected")
    elif status == "SKIP":
        print(f"[{YELLOW}SKIP{RESET}] {provider:<10} : {message}")
    else:
        print(f"[{RED}FAIL{RESET}] {provider:<10} : {message}")

async def check_openai(api_key=None):
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        return "SKIP", "No API Key found"
    try:
        # Simple check without making a full request if possible, or a very cheap one
        # For now, we'll just check if the library loads and key is present. 
        # To really test, we'd need to make a call.
        from openai import OpenAI
        client = OpenAI(api_key=key)
        client.models.list() # Lightweight call
        return "OK", ""
    except Exception as e:
        return "FAIL", str(e)

async def check_groq(api_key=None):
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        return "SKIP", "No API Key found"
    try:
        client = Groq(api_key=key)
        client.models.list()
        return "OK", ""
    except Exception as e:
        return "FAIL", str(e)

async def check_gemini(api_key=None):
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        return "SKIP", "No API Key found"
    try:
        genai.configure(api_key=key)
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        model = genai.GenerativeModel(model_name)
        # Use count_tokens for a cheaper/lighter check
        try:
            response = model.count_tokens("Hi")
            return "OK", ""
        except Exception as e:
            if "429" in str(e):
                return "FAIL", "Rate limit exceeded (429). Try a different model (e.g. Flash) or wait."
            raise e
    except Exception as e:
        return "FAIL", str(e)

async def check_tavily(api_key=None):
    key = api_key or os.getenv("TAVILY_API_KEY")
    if not key:
        return "SKIP", "No API Key found"
    try:
        # Manual request since we might not have the SDK installed or want to keep it light
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={"api_key": key, "query": "test", "search_depth": "basic", "max_results": 1},
                timeout=10.0
            )
            if resp.status_code == 200:
                return "OK", ""
            else:
                return "FAIL", f"Status {resp.status_code}"
    except Exception as e:
        return "FAIL", str(e)

async def main():
    print("Verifying AI Connectivity...\n")
    
    # OpenAI
    status, msg = await check_openai()
    print_status("OpenAI", status, msg)

    # Groq
    status, msg = await check_groq()
    print_status("Groq", status, msg)

    # Gemini
    status, msg = await check_gemini()
    print_status("Gemini", status, msg)

    # Tavily
    status, msg = await check_tavily()
    print_status("Tavily", status, msg)

    print("\nDone.")

def get_openai_models(api_key):
    if not api_key: return []
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        return [m.id for m in client.models.list()]
    except: return []

def get_groq_models(api_key):
    if not api_key: return []
    try:
        client = Groq(api_key=api_key)
        return [m.id for m in client.models.list().data]
    except: return []

def get_gemini_models(api_key):
    if not api_key: return []
    try:
        genai.configure(api_key=api_key)
        return [m.name.replace("models/", "") for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
    except: return []

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    # If running from root (as siga.sh does), path is backend/.env
    # If running from backend dir, path is .env
    if os.path.exists("backend/.env"):
        load_dotenv("backend/.env")
    elif os.path.exists(".env"):
        load_dotenv(".env")
    else:
        # Fallback or maybe it's in parent?
        load_dotenv()
        
    asyncio.run(main())
