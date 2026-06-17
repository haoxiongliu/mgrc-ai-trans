from mgrc_ai_trans.config import (
    DEFAULT_MODEL,
    provider_for_model,
    request_overrides_for_model,
    resolve_api_config,
)


def test_provider_for_supported_models():
    assert DEFAULT_MODEL == "deepseek-v4-flash"
    assert provider_for_model("deepseek-v4-flash") == "deepseek"
    assert provider_for_model("kimi-k2.6") == "moonshot"


def test_request_overrides_for_supported_models():
    assert request_overrides_for_model("deepseek-v4-flash") == {}
    assert request_overrides_for_model("kimi-k2.6") == {"temperature": 1.0}


def test_resolve_api_config_from_environment(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-deepseek-key")
    monkeypatch.delenv("DEEPSEEK_BASE_URL", raising=False)
    monkeypatch.setenv("MOONSHOT_API_KEY", "test-moonshot-key")
    monkeypatch.setenv("MOONSHOT_BASE_URL", "https://moonshot.example/v1")

    deepseek = resolve_api_config(model="deepseek-v4-flash")
    moonshot = resolve_api_config(model="kimi-k2.6")

    assert deepseek.api_key == "test-deepseek-key"
    assert deepseek.base_url == "https://api.deepseek.com/v1"
    assert moonshot.api_key == "test-moonshot-key"
    assert moonshot.base_url == "https://moonshot.example/v1"
