import os
from dataclasses import dataclass

from dotenv import load_dotenv


DEFAULT_MODEL = "deepseek-v4-flash"

PROVIDER_ENV = {
    "deepseek": {
        "api_key": "DEEPSEEK_API_KEY",
        "base_url": "DEEPSEEK_BASE_URL",
        "default_base_url": "https://api.deepseek.com/v1",
    },
    "moonshot": {
        "api_key": "MOONSHOT_API_KEY",
        "base_url": "MOONSHOT_BASE_URL",
        "default_base_url": "https://api.moonshot.cn/v1",
    },
}


@dataclass(frozen=True)
class APIConfig:
    api_key: str
    base_url: str
    provider: str


def load_env() -> None:
    load_dotenv()


def provider_for_model(model: str) -> str | None:
    model_lower = model.lower()
    if model_lower.startswith("deepseek"):
        return "deepseek"
    if model_lower.startswith("kimi") or model_lower.startswith("moonshot"):
        return "moonshot"
    return None


def request_overrides_for_model(model: str) -> dict:
    if model.lower() == "kimi-k2.6":
        return {"temperature": 1.0}
    return {}


def resolve_api_config(
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
    base_url: str | None = None,
) -> APIConfig:
    load_env()
    provider = provider_for_model(model)
    if not provider:
        if not api_key or not base_url:
            raise ValueError(
                f"Cannot infer API provider for model {model!r}; pass both api_key and base_url."
            )
        return APIConfig(api_key=api_key, base_url=base_url, provider="custom")

    env = PROVIDER_ENV[provider]
    resolved_api_key = api_key or os.getenv(env["api_key"])
    resolved_base_url = base_url or os.getenv(env["base_url"]) or env["default_base_url"]

    if not resolved_api_key:
        raise ValueError(f"Missing {env['api_key']} for model {model!r}.")

    return APIConfig(
        api_key=resolved_api_key,
        base_url=resolved_base_url,
        provider=provider,
    )
