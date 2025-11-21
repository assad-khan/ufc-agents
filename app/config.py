import os
from typing import Dict
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Agent to model mapping - optimized models per user requirements
AGENT_MODELS = {
    "tape_study": "claude-3-7-sonnet-20250219",
    "stats_trends": "gpt-5",
    "news_weighins": "gemini-2.5-pro",
    "style_matchup": "claude-3-7-sonnet-20250219",
    "market_odds": "gpt-5-mini",
    "judge": "gpt-5",
    "risk_scorer": "gpt-5-mini",
    "consistency_checker": "claude-3-5-haiku-20241022"
}

# Agent temperature settings for custom control
AGENT_TEMPERATURES = {
    "tape_study": 0.2,        # Claude 3.7 Sonnet temperature
    "stats_trends": 0.1,      # GPT-5 Thinking temperature
    "news_weighins": 0.1,     # Gemini-2.5-pro temperature
    "style_matchup": 0.2,     # Claude 3.7 Sonnet temperature
    "market_odds": 0.0,       # GPT-5 mini temperature
    "judge": 0.0,             # GPT-5 Thinking (JSON mode) temperature
    "risk_scorer": 0.0,       # GPT-5 mini temperature
    "consistency_checker": 0.05  # Claude 3.7 Haiku temperature
}

# Agent top-p settings for custom control
AGENT_TOP_PS = {
    "tape_study": 0.9,        # Claude 3.7 Sonnet top-p
    "stats_trends": 0.9,      # GPT-5 Thinking top-p
    "news_weighins": 0.9,     # Gemini-2.5-pro top-p
    "style_matchup": 0.9,     # Claude 3.7 Sonnet top-p
    "market_odds": 0.8,       # GPT-5 mini top-p
    "judge": 0.5,             # GPT-5 Thinking (JSON mode) top-p for precision
    "risk_scorer": 0.8,       # GPT-5 mini top-p
    "consistency_checker": 0.7  # Claude 3.7 Haiku top-p for balanced precision/creativity
}

# API Keys
API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    "google": os.getenv("GOOGLE_API_KEY"),
    "serper": os.getenv("SERPER_API_KEY")
}

def get_model_for_agent(agent_type: str) -> str:
    model_name = AGENT_MODELS.get(agent_type, "gpt-4o")
    logger.info(f"Using model {model_name} for agent {agent_type}")
    return model_name 

def get_temperature_for_agent(agent_type: str) -> float:
    return AGENT_TEMPERATURES.get(agent_type, 0.1)  # default temperature

def get_top_p_for_agent(agent_type: str) -> float:
    return AGENT_TOP_PS.get(agent_type, 0.9)  # default top-p

def get_api_key(provider: str, runtime_keys: Dict[str, str] = None) -> str:
    """Get API key either from runtime keys or environment variables"""
    if runtime_keys and provider in runtime_keys:
        return runtime_keys[provider]
    return API_KEYS.get(provider)


def set_runtime_api_keys(runtime_keys: Dict[str, str] = None):
    """Temporarily set environment variables for runtime API keys"""
    if runtime_keys:
        env_mapping = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
            "serper": "SERPER_API_KEY"
        }
        for provider, key in runtime_keys.items():
            env_var = env_mapping.get(provider)
            if env_var and key:
                os.environ[env_var] = key
                logger.info(f"Set runtime API key for {provider}")
