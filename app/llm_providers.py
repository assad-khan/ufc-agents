from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import get_api_key
from typing import Dict

def get_llm(model_name: str, temperature: float = 0.1, runtime_keys: Dict[str, str] = None):
    if model_name.startswith("gpt"):
        return ChatOpenAI(
            model=model_name,
            api_key=get_api_key("openai", runtime_keys),
            temperature=temperature,
            reasoning={ "effort": "medium" },
            verbose=True,
        )
    elif model_name.startswith("claude"):
        return ChatAnthropic(
            model=model_name,
            api_key=get_api_key("anthropic", runtime_keys),
            temperature=temperature,
            max_tokens=4096  # Ensure adequate response length
        )
    elif model_name.startswith("gemini"):
        return ChatGoogleGenerativeAI(
            model=model_name,
            api_key=get_api_key("google", runtime_keys),
            temperature=temperature
        )
    else:
        # Default to GPT-4o
        return ChatOpenAI(
            model="gpt-4o",
            api_key=get_api_key("openai", runtime_keys),
            temperature=temperature
        )
