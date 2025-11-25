import os
import sys
from dotenv import load_dotenv
import asyncio
import httpx

# ... (imports)

# Remove google.generativeai import
# import google.generativeai as genai

# ...

async def check_gemini(api_key=None):
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        return "SKIP", "No API Key found"
    try:
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                json={"contents": [{"parts": [{"text": "Hi"}]}]},
                timeout=10.0
            )
            if resp.status_code == 200:
                return "OK", ""
            elif resp.status_code == 429:
                return "FAIL", "Rate limit exceeded (429)."
            else:
                return "FAIL", f"Status {resp.status_code}: {resp.text[:100]}"
    except Exception as e:
        return "FAIL", str(e)

# ...

def get_gemini_models(api_key):
    if not api_key: return []
    try:
        with httpx.Client() as client:
            resp = client.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}")
            if resp.status_code == 200:
                data = resp.json()
                return [m['name'].replace("models/", "") for m in data.get('models', []) if "generateContent" in m.get('supportedGenerationMethods', [])]
            return []
    except: return []

async def check_groq(api_key=None):
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        return "SKIP", "No API Key found"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=10.0
            )
            if resp.status_code == 200:
                return "OK", ""
            else:
                return "FAIL", f"Status {resp.status_code}"
    except Exception as e:
        return "FAIL", str(e)

# ...

def get_groq_models(api_key):
    if not api_key: return []
    try:
        with httpx.Client() as client:
            resp = client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            if resp.status_code == 200:
                data = resp.json()
                return [m['id'] for m in data.get('data', [])]
            return []
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
