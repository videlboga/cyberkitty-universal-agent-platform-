from loguru import logger

class PluginBase:
    def __init__(self, config=None):
        self.config = config or {}
        self.logger = logger.bind(plugin_name=self.__class__.__name__)

    def on_event(self, event):
        """Обработка события интеграции (LLM, RAG, CRM и др.)"""
        return {"status": "ok", "event": event}

    def healthcheck(self):
        """Проверка работоспособности плагина"""
        return True 