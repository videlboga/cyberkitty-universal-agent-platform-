from app.plugins.plugin import PluginBase

class NewsPlugin(PluginBase):
    def latest(self, topic=None):
        return {"status": "ok", "news": [
            {"title": "Главная новость дня", "source": "NewsAPI", "topic": topic or "general"},
            {"title": "Вторая новость", "source": "RSS", "topic": topic or "general"}
        ], "mode": "mock"}
    def search(self, query):
        return {"status": "ok", "news": [
            {"title": f"Новость по запросу: {query}", "source": "NewsAPI"}
        ], "mode": "mock"}
    def healthcheck(self):
        return True 