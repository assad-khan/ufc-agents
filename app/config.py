import os
from typing import Dict
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Agent to model mapping - optimized models per user requirements
AGENT_MODELS = {
    "tape_study": "claude-3-7-sonnet-20250219",   
    "stats_trends": "gpt-5",              
    "news_weighins": "gpt-5",             
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
    "news_weighins": 0.1,     # GPT-5 Thinking temperature
    "style_matchup": 0.2,     # Claude 3.7 Sonnet temperature
    "market_odds": 0.0,       # GPT-5 mini temperature
    "judge": 0.0,             # GPT-5 Thinking (JSON mode) temperature
    "risk_scorer": 0.0,       # GPT-5 mini temperature
    "consistency_checker": 0.05  # Claude 3.7 Haiku temperature
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

def get_api_key(provider: str) -> str:
    return API_KEYS.get(provider)
