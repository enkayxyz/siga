import os
import time
import asyncio
from typing import List, Optional, Dict
from .models import Company, Subsidiary, Location, Financials, ResearchUsage
from .database import db
# from groq import Groq
# from geopy.geocoders import Nominatim
# from geopy.exc import GeocoderTimedOut

# ...

class GroqProvider(LLMProvider):
    def __init__(self, api_key, model_name):
        super().__init__("groq")
        self.api_key = api_key
        self.model_name = model_name or "mixtral-8x7b-32768"
    
    async def _call_api(self, prompt: str) -> (str, int):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=30.0
                )
                if resp.status_code != 200:
                    print(f"Groq Error: {resp.status_code} - {resp.text}")
                    return f"Error: {resp.status_code}", 0
                
                data = resp.json()
                content = data['choices'][0]['message']['content']
                tokens = data['usage']['total_tokens']
                return content, tokens
        except Exception as e:
            print(f"Groq Error: {e}")
            return "Error generating response from Groq.", 0

# ...

    async def _geocode_locations(self, company: Company) -> Company:
        # Use Nominatim REST API directly via httpx
        cache = {}

        async def get_coords(city, country):
            key = f"{city}, {country}"
            if key in cache: return cache[key]
            if city == "Unknown" or country == "Unknown": return None
            
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        "https://nominatim.openstreetmap.org/search",
                        params={"city": city, "country": country, "format": "json", "limit": 1},
                        headers={"User-Agent": "siga_agent_v1"},
                        timeout=5.0
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if data:
                            lat = float(data[0]['lat'])
                            lon = float(data[0]['lon'])
                            coords = [lat, lon]
                            cache[key] = coords
                            return coords
            except Exception as e:
                print(f"Geocoding failed for {key}: {e}")
            return None

        # Geocode HQ
        if company.hq_location:
            coords = await get_coords(company.hq_location.city, company.hq_location.country)
            if coords:
                company.hq_location.coordinates = coords

        # Geocode Subsidiaries
        for sub in company.subsidiaries:
            if sub.location:
                coords = await get_coords(sub.location.city, sub.location.country)
                if coords:
                    sub.location.coordinates = coords
        
        return company

    def _mock_data(self, company_name: str) -> Company:
        return Company(
            name=company_name,
            hq_location=Location(city="San Francisco", country="USA"),
            subsidiaries=[
                Subsidiary(name=f"{company_name} Labs", location=Location(city="Paris", country="France"), type="R&D"),
                Subsidiary(name=f"{company_name} Ventures", location=Location(city="New York", country="USA"), type="Investment")
            ],
            total_revenue="50B"
        )

agent = ResearchAgent()
