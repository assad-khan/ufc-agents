import os
from typing import Dict
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Agent to model mapping - updated with correct model names
AGENT_MODELS = {
    "tape_study": "claude-3-7-sonnet-20250219", 
    # "stats_trends": "gemini-2.5-flash",
    "stats_trends": "claude-3-7-sonnet-20250219",
    "news_weighins": "gpt-4o",
    "style_matchup": "claude-3-7-sonnet-20250219",  
    "market_odds": "gpt-4o",
    "judge": "gpt-4o",
    "risk_scorer": "claude-3-7-sonnet-20250219", 
    "consistency_checker": "gpt-4o"
}

# API Keys
API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    "google": os.getenv("GOOGLE_API_KEY")
}

def get_model_for_agent(agent_type: str) -> str:
    model_name = AGENT_MODELS.get(agent_type, "gpt-4o")
    logger.info(f"Using model {model_name} for agent {agent_type}")
    return model_name 

def get_api_key(provider: str) -> str:
    return API_KEYS.get(provider)
