from app.plugins.mock_llm_plugin import MockLLMPlugin

def test_on_event():
    plugin = MockLLMPlugin()
    event = {"prompt": "Привет, LLM!"}
    result = plugin.on_event(event)
    assert result["status"] == "ok"
    assert "Mock LLM ответ на: Привет, LLM!" in result["response"]

def test_healthcheck():
    plugin = MockLLMPlugin()
    assert plugin.healthcheck() is True 