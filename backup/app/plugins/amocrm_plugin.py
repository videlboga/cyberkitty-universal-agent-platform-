from app.plugins.plugin import PluginBase

class AmoCRMPlugin(PluginBase):
    def create_lead(self, name, status="new"):
        return {"status": "ok", "lead": {"id": 1, "name": name, "status": status, "mode": "mock"}}
    def get_leads(self):
        return {"status": "ok", "leads": [
            {"id": 1, "name": "Тестовый лид", "status": "new"},
            {"id": 2, "name": "Демо", "status": "in_progress"}
        ]}
    def healthcheck(self):
        return True 