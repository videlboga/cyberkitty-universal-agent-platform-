class PluginBase:
    def __init__(self, config=None):
        self.config = config or {}

    def on_event(self, event):
        """Обработка события интеграции (LLM, RAG, CRM и др.)"""
        return {"status": "ok", "event": event}

    def healthcheck(self):
        """Проверка работоспособности плагина"""
        return True 