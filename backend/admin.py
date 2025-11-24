import os
from pydantic import BaseModel
from typing import Optional

ENV_FILE = ".env"
BACKEND_ENV_FILE = "backend/.env"

class Settings(BaseModel):
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    groq_api_key: Optional[str] = None
    groq_model: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    tavily_api_key: Optional[str] = None
    llm_provider: Optional[str] = None

def get_settings() -> Settings:
    # Reload env vars from file to ensure freshness
    settings = {}
    
    # Check for backend/.env first (CLI writes there)
    env_path = BACKEND_ENV_FILE if os.path.exists(BACKEND_ENV_FILE) else ENV_FILE
    
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    settings[key.lower()] = value
    
    return Settings(
        openai_api_key=settings.get("openai_api_key"),
        openai_model=settings.get("openai_model"),
        groq_api_key=settings.get("groq_api_key"),
        groq_model=settings.get("groq_model"),
        gemini_api_key=settings.get("gemini_api_key"),
        gemini_model=settings.get("gemini_model"),
        tavily_api_key=settings.get("tavily_api_key"),
        llm_provider=settings.get("llm_provider"),
    )

def save_settings(new_settings: Settings):
    current = get_settings().dict()
    update_data = new_settings.dict(exclude_unset=True)
    
    # Merge
    for k, v in update_data.items():
        if v is not None:
            current[k] = v
            
    # Write to file
    lines = []
    for k, v in current.items():
        if v:
            lines.append(f"{k.upper()}={v}\n")
    
    # Determine which file to write to
    env_path = BACKEND_ENV_FILE if os.path.exists(BACKEND_ENV_FILE) else ENV_FILE
            
    with open(env_path, "w") as f:
        f.writelines(lines)
        
    # Update os.environ
    for k, v in current.items():
        if v:
            os.environ[k.upper()] = v

def get_logs(log_type: str = "backend") -> str:
    # backend.log is in root (../backend.log relative to backend dir? No, running from root)
    # The app is running from root.
    # backend/main.py is executed.
    # Logs are in root: backend.log, frontend.log
    
    filename = "backend.log" if log_type == "backend" else "frontend.log"
    
    # We are in backend/ directory context when importing?
    # No, uvicorn runs from root: uvicorn backend.main:app
    # So CWD is root.
    
    if os.path.exists(filename):
        with open(filename, "r") as f:
            # Read last 100 lines maybe?
            lines = f.readlines()
            return "".join(lines[-200:]) # Return last 200 lines
    return "No logs found."
