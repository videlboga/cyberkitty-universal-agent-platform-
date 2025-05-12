import os
import requests

class AmoCRMClient:
    def __init__(self, base_url=None, access_token=None):
        self.base_url = base_url or os.getenv("AMO_BASE_URL")
        self.access_token = access_token or os.getenv("AMO_ACCESS_TOKEN")
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def get_fields(self, entity="leads"):
        """
        Получить структуру всех полей для сущности (leads, contacts, companies и т.д.)
        Возвращает список dict с id, name, type, code, enums, is_required, is_system, origin
        """
        url = f"{self.base_url}/api/v4/{entity}/custom_fields"
        resp = requests.get(url, headers=self.headers)
        resp.raise_for_status()
        data = resp.json()
        fields = []
        for f in data.get('_embedded', {}).get('custom_fields', []):
            enums = []
            if 'enums' in f and isinstance(f['enums'], list):
                enums = [{"id": e.get("id"), "value": e.get("value")} for e in f["enums"]]
            elif 'enums' in f and isinstance(f['enums'], dict):
                enums = [{"id": k, "value": v} for k, v in f["enums"].items()]
            fields.append({
                "id": f.get("id"),
                "name": f.get("name"),
                "type": f.get("type"),
                "code": f.get("code"),
                "enums": enums,
                "is_required": f.get("is_required", False),
                "is_system": f.get("is_system", False),
                "origin": f.get("origin") or f.get("code")
            })
        return fields 