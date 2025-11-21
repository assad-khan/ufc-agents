from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import get_api_key
from typing import Dict

def get_llm(model_name: str, temperature: float = 0.1, top_p: float = None, runtime_keys: Dict[str, str] = None):
    if model_name.startswith("gpt"):
        config = {
            "model": model_name,
            "api_key": get_api_key("openai", runtime_keys),
            "temperature": temperature,
            "reasoning": { "effort": "medium" },
            "verbose": True,
        }
        if top_p is not None:
            config["top_p"] = top_p
        return ChatOpenAI(**config)
    elif model_name.startswith("claude"):
        config = {
            "model": model_name,
            "api_key": get_api_key("anthropic", runtime_keys),
            "temperature": temperature,
            "max_tokens": 4096  # Ensure adequate response length
        }
        if top_p is not None:
            config["top_p"] = top_p
        return ChatAnthropic(**config)
    elif model_name.startswith("gemini"):
        config = {
            "model": model_name,
            "api_key": get_api_key("google", runtime_keys),
            "temperature": temperature,
        }
        if top_p is not None:
            config["top_p"] = top_p
        return ChatGoogleGenerativeAI(**config)
    else:
        # Default to GPT-4o
        config = {
            "model": "gpt-4o",
            "api_key": get_api_key("openai", runtime_keys),
            "temperature": temperature,
        }
        if top_p is not None:
            config["top_p"] = top_p
