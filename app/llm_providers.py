from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import get_api_key

def get_llm(model_name: str, temperature: float = 0.1):
    if model_name.startswith("gpt"):
        return ChatOpenAI(
            model=model_name,
            api_key=get_api_key("openai"),
            temperature=temperature,
            reasoning={ "effort": "medium" },
            verbose=True
        )
    elif model_name.startswith("claude"):
        return ChatAnthropic(
            model=model_name,
            api_key=get_api_key("anthropic"),
            temperature=temperature,
            max_tokens=4096  # Ensure adequate response length
        )
    elif model_name.startswith("gemini"):
        return ChatGoogleGenerativeAI(
            model=model_name,
            api_key=get_api_key("google"),
            temperature=temperature
        )
    else:
        # Default to GPT-4o
        return ChatOpenAI(
            model="gpt-4o",
            api_key=get_api_key("openai"),
            temperature=temperature
        )
