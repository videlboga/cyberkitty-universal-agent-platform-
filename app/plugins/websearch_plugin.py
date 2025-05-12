from app.plugins.plugin import PluginBase

class WebSearchPlugin(PluginBase):
    def search(self, query):
        return {"status": "ok", "results": [
            {"title": "Wikipedia", "url": "https://ru.wikipedia.org/wiki/" + query.replace(" ", "_"), "snippet": "Статья из Википедии по запросу: " + query},
            {"title": "Google Search", "url": "https://www.google.com/search?q=" + query, "snippet": "Результаты Google для: " + query}
        ], "mode": "mock"}
    def healthcheck(self):
        return True 