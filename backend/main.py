from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import json
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load env from backend/.env if it exists (CLI/Setup writes there)
# MUST be done before importing agent, as it initializes on import
if os.path.exists("backend/.env"):
    load_dotenv("backend/.env")
else:
    load_dotenv()

from .agent import agent, Company
from .admin import get_settings, save_settings, get_logs, Settings
from .verify_ai import check_openai, check_groq, check_gemini, check_tavily, get_openai_models, get_groq_models, get_gemini_models

app = FastAPI(title="Siga Agent API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    company_name: str
    forensic_mode: bool = False

@app.get("/")
def read_root():
    return {"message": "Siga Agent API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/settings", response_model=Settings)
def read_settings():
    return get_settings()

@app.post("/settings")
def update_settings_endpoint(settings: Settings):
    save_settings(settings)
    agent.reload_config()
    return {"status": "updated"}

@app.get("/logs/{log_type}")
def read_logs(log_type: str):
    return {"logs": get_logs(log_type)}

@app.get("/verify/{provider}")
async def verify_provider(provider: str):
    settings = get_settings() # Get fresh settings from file
    provider = provider.lower()
    
    if provider == "openai":
        status, msg = await check_openai(settings.openai_api_key)
    elif provider == "groq":
        status, msg = await check_groq(settings.groq_api_key)
    elif provider == "gemini":
        status, msg = await check_gemini(settings.gemini_api_key)
    elif provider == "tavily":
        status, msg = await check_tavily(settings.tavily_api_key)
    else:
        raise HTTPException(status_code=400, detail="Unknown provider")
    
    return {"provider": provider, "status": status, "message": msg}

@app.get("/models/{provider}")
def list_models(provider: str):
    settings = get_settings()
    provider = provider.lower()
    models = []
    
    if provider == "openai":
        models = get_openai_models(settings.openai_api_key)
    elif provider == "groq":
        models = get_groq_models(settings.groq_api_key)
    elif provider == "gemini":
        models = get_gemini_models(settings.gemini_api_key)
    else:
        raise HTTPException(status_code=400, detail="Unknown provider")
        
    return {"provider": provider, "models": models}

@app.post("/research")
async def research_company(request: ResearchRequest):
    async def event_generator():
        async for event in agent.research_company(request.company_name, request.forensic_mode):
            yield json.dumps(event) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson")
