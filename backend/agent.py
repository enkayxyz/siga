import os
import time
import asyncio
from typing import List, Optional, Dict
from .models import Company, Subsidiary, Location, Financials, ResearchUsage
from .database import db
from .admin import get_settings
import google.generativeai as genai
from groq import Groq
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
# import cerebras.cloud_sdk as cerebras # Placeholder for Cerebras SDK if available, or use HTTP

# Rate Limiting Configuration
RATE_LIMITS = {
    "openai": 3,      # requests per minute
    "groq": 30,       # fast inference
    "gemini": 15,     # free tier limits
    "cerebras": 10    # placeholder
}

class LLMProvider:
    def __init__(self, provider_name: str):
        self.name = provider_name
        self.last_request_time = 0
        self.min_interval = 60.0 / RATE_LIMITS.get(provider_name, 5)

    async def generate(self, prompt: str) -> (str, int):
        # Rate Limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            wait_time = self.min_interval - elapsed
            print(f"[{self.name}] Rate limit hit. Waiting {wait_time:.2f}s...")
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
        return await self._call_api(prompt)

    async def _call_api(self, prompt: str) -> (str, int):
        raise NotImplementedError

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key, model_name):
        super().__init__("openai")
        # self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
    
    async def _call_api(self, prompt: str) -> (str, int):
        # Mock implementation for now
        # In real implementation: usage = response.usage.total_tokens
        return f"OpenAI Response: {prompt[:50]}...", 100

class GroqProvider(LLMProvider):
    def __init__(self, api_key, model_name):
        super().__init__("groq")
        self.client = Groq(api_key=api_key)
        self.model_name = model_name or "mixtral-8x7b-32768"
    
    async def _call_api(self, prompt: str) -> (str, int):
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
            )
            content = completion.choices[0].message.content
            tokens = completion.usage.total_tokens if completion.usage else 0
            return content, tokens
        except Exception as e:
            print(f"Groq Error: {e}")
            return "Error generating response from Groq.", 0

class GeminiProvider(LLMProvider):
    def __init__(self, api_key, model_name):
        super().__init__("gemini")
        genai.configure(api_key=api_key)
        self.model_name = model_name or "gemini-1.5-flash"
        self.model = genai.GenerativeModel(self.model_name)

    async def _call_api(self, prompt: str) -> (str, int):
        try:
            response = self.model.generate_content(prompt)
            # Estimate tokens if not provided (Gemini doesn't always return usage in simple call)
            # But we can use count_tokens API if needed. For now, rough estimate: char / 4
            tokens = len(response.text) // 4 
            return response.text, tokens
        except Exception as e:
            print(f"Gemini Error: {e}")
            return "Error generating response from Gemini.", 0

class ResearchAgent:
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.active_provider = "openai"
        self._init_providers()

    def _init_providers(self):
        settings = get_settings()
        self.active_provider = settings.llm_provider or "openai"
        
        if settings.openai_api_key:
            self.providers["openai"] = OpenAIProvider(settings.openai_api_key, settings.openai_model)
        if settings.groq_api_key:
            self.providers["groq"] = GroqProvider(settings.groq_api_key, settings.groq_model)
        if settings.gemini_api_key:
            self.providers["gemini"] = GeminiProvider(settings.gemini_api_key, settings.gemini_model)

    def reload_config(self):
        self._init_providers()

    async def research_company(self, company_name: str, forensic_mode: bool = False):
        # Refresh config on every request
        self._init_providers()
        
        usage = ResearchUsage()
        
        mode_label = "FORENSIC MODE" if forensic_mode else "STANDARD MODE"
        yield {"type": "status", "message": f"Initializing {mode_label} research for {company_name}..."}
        print(f"Researching {company_name} ({mode_label}) using {self.active_provider}...")
        
        # 2. Perform Recursive Search
        settings = get_settings()
        tavily_key = settings.tavily_api_key
        if not tavily_key:
            yield {"type": "error", "message": "Tavily API Key is missing."}
            raise Exception("Tavily API Key is missing. Please configure it in Settings.")
            
        # Step 2a: General Search
        yield {"type": "status", "message": "Searching for general corporate info (HQ, Revenue)..."}
        general_results = await self._search_web(f"{company_name} HQ location revenue annual report 2024", tavily_key)
        usage.tavily_calls += 1
        
        # Step 2b: SEC Exhibit 21.1 Search
        yield {"type": "status", "message": "Searching SEC Database for Exhibit 21.1 (Subsidiaries)..."}
        sec_results = await self._search_web(f"{company_name} 10-K Exhibit 21.1 list of subsidiaries", tavily_key)
        usage.tavily_calls += 1

        # Step 2c: International/Major Subsidiaries Search
        if not forensic_mode:
            yield {"type": "status", "message": "Searching for international legal entities..."}
            intl_results = await self._search_web(f"list of {company_name} major subsidiaries Europe Asia legal entities", tavily_key)
            usage.tavily_calls += 1
        else:
            # FORENSIC MODE: Region Sweeps
            regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East & Africa"]
            intl_results = ""
            for region in regions:
                yield {"type": "status", "message": f"Forensic Sweep: Searching {region}..."}
                region_res = await self._search_web(f"{company_name} subsidiaries offices presence in {region} list", tavily_key)
                intl_results += f"\n=== {region.upper()} SEARCH RESULTS ===\n{region_res}\n"
                usage.tavily_calls += 1

        # Step 2d: News & Expansion Search
        yield {"type": "status", "message": "Analyzing recent news for market expansion..."}
        news_results = await self._search_web(f"{company_name} expansion news new markets 2024", tavily_key)
        usage.tavily_calls += 1

        # Step 2e: Earnings Call Search
        yield {"type": "status", "message": "Checking earnings call transcripts..."}
        earnings_results = await self._search_web(f"{company_name} earnings call transcript international growth", tavily_key)
        usage.tavily_calls += 1
        
        # Combine results
        combined_results = f"""
        === GENERAL SEARCH RESULTS ===
        {general_results}
        
        === SEC EXHIBIT 21.1 SEARCH RESULTS ===
        {sec_results}

        === INTERNATIONAL/REGIONAL SEARCH RESULTS ===
        {intl_results}

        === NEWS & EXPANSION RESULTS ===
        {news_results}

        === EARNINGS CALL INSIGHTS ===
        {earnings_results}
        """
        
        # 3. Extract Info with LLM
        provider = self.providers.get(self.active_provider)
        if not provider:
            yield {"type": "error", "message": f"Provider {self.active_provider} not configured."}
            raise Exception(f"Provider {self.active_provider} is not configured.")
        
        yield {"type": "status", "message": f"Analyzing data with {self.active_provider}..."}
        company_data, tokens = await self._extract_info(company_name, combined_results, provider)
        usage.llm_tokens += tokens
        
        # FORENSIC MODE: Gap Filling
        if forensic_mode:
            yield {"type": "status", "message": "Forensic Analysis: Identifying data gaps..."}
            # Find subsidiaries with unknown locations
            unknowns = [sub for sub in company_data.subsidiaries if not sub.location or sub.location.country == "Unknown"]
            # Limit to top 5 to avoid excessive time/cost
            for i, sub in enumerate(unknowns[:5]):
                yield {"type": "status", "message": f"Gap Filling: Researching location for {sub.name}..."}
                query = f"{sub.name} {company_name} headquarters location address"
                sub_res = await self._search_web(query, tavily_key)
                usage.tavily_calls += 1
                
                # Mini-extraction for this subsidiary
                prompt = f"""
                Analyze this search result for subsidiary '{sub.name}' of '{company_name}'.
                Find its City and Country.
                Result: {sub_res}
                Return JSON: {{ "city": "City", "country": "Country" }}
                """
                try:
                    resp_text, sub_tokens = await provider.generate(prompt)
                    usage.llm_tokens += sub_tokens
                    import json
                    loc_data = json.loads(resp_text.replace("```json", "").replace("```", "").strip())
                    if loc_data.get("country") and loc_data.get("country") != "Unknown":
                        sub.location = Location(city=loc_data.get("city"), country=loc_data.get("country"))
                        sub.source += " (Gap Filled)"
                except Exception as e:
                    print(f"Gap filling failed for {sub.name}: {e}")

        # Calculate estimated cost
        usage.estimated_cost = (usage.tavily_calls * 0.01) + (usage.llm_tokens / 1000 * 0.01)
        company_data.usage = usage

        # 4. Geocode Locations
        yield {"type": "status", "message": "Geocoding locations for global map..."}
        company_data = await self._geocode_locations(company_data)

        # 5. Save to Memory
        db.save_company(company_data)
        
        yield {"type": "status", "message": "Research complete."}
        yield {"type": "result", "data": company_data.dict()}

    async def _search_web(self, query: str, api_key: str) -> str:
        print(f"Searching web for: {query}")
        import httpx
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": api_key,
                        "query": query,
                        "search_depth": "basic",
                        "max_results": 5,
                        "include_answer": True
                    },
                    timeout=15.0
                )
                resp.raise_for_status()
                data = resp.json()
                # Combine answer and results
                context = f"Answer: {data.get('answer', '')}\n\nResults:\n"
                for result in data.get("results", []):
                    context += f"- {result['title']}: {result['content']}\n"
                return context
            except Exception as e:
                print(f"Search failed: {e}")
                return f"Error searching for {query}: {str(e)}"

    async def _extract_info(self, company_name: str, search_results: str, provider: LLMProvider) -> (Company, int):
        print("Extracting info with LLM...")
        prompt = f"""
        You are a senior financial analyst. Your task is to analyze the provided search results for '{company_name}' and extract detailed corporate information.
        
        Focus specifically on:
        1. **HQ Location**: City and Country.
        2. **Total Revenue**: Most recent annual revenue available (e.g. "383 Billion USD (2023)").
        3. **Subsidiaries**: This is the MOST IMPORTANT part. 
           - Look specifically for "Exhibit 21.1" data in the search results, which lists significant subsidiaries.
           - Extract as many subsidiaries as possible (aim for 20-50+ if available).
           - Include international entities, holding companies, and operating brands.
           - Do not limit yourself to just the "famous" ones.
           - For each, provide the Name, Location (if found, else "Unknown"), Type (e.g. Tech, Retail, Holding, AI), and **Source** (e.g. "SEC Filing", "News", "General Search").

        Search Results:
        {search_results}

        Return ONLY a valid JSON object matching this schema:
        {{
            "name": "{company_name}",
            "hq_location": {{ "city": "City", "country": "Country" }},
            "total_revenue": "Revenue String",
            "subsidiaries": [
                {{ "name": "Sub Name", "location": {{ "city": "City", "country": "Country" }}, "type": "Type", "source": "Source" }}
            ]
        }}
        
        Rules:
        - If information is missing, make a reasonable estimate based on context or use "Unknown".
        - Do NOT use markdown formatting (no ```json).
        - Ensure valid JSON.
        """
        
        response_text, tokens = await provider.generate(prompt)
        # Clean response
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        import json
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            print(f"JSON Decode Error. Raw response: {response_text}")
            raise Exception("Failed to parse LLM response as JSON.")
        
        company = Company(
            name=data.get("name", company_name),
            hq_location=Location(**data.get("hq_location", {"city": "Unknown", "country": "Unknown"})),
            total_revenue=data.get("total_revenue", "Unknown"),
            subsidiaries=[
                Subsidiary(
                    name=sub.get("name"),
                    location=Location(**sub.get("location", {"city": "Unknown", "country": "Unknown"})),
                    type=sub.get("type", "Unknown"),
                    source=sub.get("source", "Unknown")
                ) for sub in data.get("subsidiaries", [])
            ]
        )
        return company, tokens

    async def _geocode_locations(self, company: Company) -> Company:
        geolocator = Nominatim(user_agent="siga_agent")
        cache = {}

        async def get_coords(city, country):
            key = f"{city}, {country}"
            if key in cache: return cache[key]
            if city == "Unknown" or country == "Unknown": return None
            
            try:
                # Run in executor to avoid blocking async loop
                loop = asyncio.get_event_loop()
                location = await loop.run_in_executor(None, lambda: geolocator.geocode(key, timeout=5))
                if location:
                    coords = [location.latitude, location.longitude]
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
