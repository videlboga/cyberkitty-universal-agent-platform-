from app.plugins.plugin import PluginBase

class MockLLMPlugin(PluginBase):
    def on_event(self, event):
        prompt = event.get("prompt", "")
        return {"status": "ok", "response": f"Mock LLM ответ на: {prompt}"}

    def healthcheck(self):
        return True 