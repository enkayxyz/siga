import json
import os
from typing import Dict, Optional
from .models import Company

DB_FILE = "siga_memory.json"

class Database:
    def __init__(self):
        self.file_path = DB_FILE
        self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def _save(self):
        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def save_company(self, company: Company):
        self.data[company.name] = company.dict()
        self._save()

    def get_company(self, name: str) -> Optional[Company]:
        data = self.data.get(name)
        if data:
            return Company(**data)
        return None

db = Database()
