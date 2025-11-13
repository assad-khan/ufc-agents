from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import get_api_key

def get_llm(model_name: str):
    if model_name.startswith("gpt"):
        return ChatOpenAI(
            model=model_name,
            api_key=get_api_key("openai"),
            temperature=0.1
        )
    elif model_name.startswith("claude"):
        return ChatAnthropic(
            model=model_name,
            api_key=get_api_key("anthropic"),
            temperature=0.1
        )
    elif model_name.startswith("gemini"):
        return ChatGoogleGenerativeAI(
            model=model_name,
            api_key=get_api_key("google"),
            temperature=0.1
        )
    else:
        # Default to GPT-4o
        return ChatOpenAI(
            model="gpt-4o",
            api_key=get_api_key("openai"),
            temperature=0.1
        )
