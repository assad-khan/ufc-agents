from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import tool
from app.config import get_model_for_agent, get_temperature_for_agent, get_api_key
from app.llm_providers import get_llm
from app.models import FightAnalysis, Card, CardAnalysis
from typing import List, Dict, Any, Optional
import requests
from loguru import logger
from app.prompts import *

# Gemini imports for direct API usage
from google import genai
from google.genai.types import GenerateContentConfig, GoogleSearch, Tool



# Serper Web Search Tool
@tool
def serper_search(query: str) -> str:
    """Search the web for fighter news, injuries, and recent updates using Serper API."""
    try:
        logger.info(f"Serper search for: {query}")
        api_key = get_api_key("serper")
        if not api_key:
            return "Serper API key not configured"

        url = "https://google.serper.dev/search"
        payload = {
            "q": query,
            "num": 5  # Get top 5 results
        }
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()
        results = data.get("organic", [])

        # Format search results
        formatted_results = []
        for i, result in enumerate(results, 1):
            title = result.get("title", "")
            link = result.get("link", "")
            snippet = result.get("snippet", "")
            formatted_results.append(f"{i}. {title} - {snippet}\n   {link}")

        results_str = "\n\n".join(formatted_results) if formatted_results else "No results found"
        logger.info(f"Serper search results: {results_str}")
        return results_str

    except Exception as e:
        logger.error(f"Serper search error: {e}")
        return f"Search error: {str(e)}"

async def run_agent(agent_type: str, system_prompt: str, card: Card, model_override: Optional[str] = None) -> str:
    logger.info(f"Starting {agent_type} agent for {len(card.fights)} fights")
    try:
        model_name = model_override if model_override else get_model_for_agent(agent_type)

        # card_info = "\n".join([
        #     f"Fight {f.fight_id}: {f.fighter1} vs {f.fighter2} ({f.weight_class})"
        #     for f in card.fights
        # ])

        # Create agent using the new API
        agent = create_agent(
            model=model_name,
            tools=[],  # No tools for analysis agents
            response_format=None,  # Text response
            system_prompt=system_prompt
        )

        user_content = f"Analyze this UFC card:\n{card}"
        result = agent.invoke({
            "messages": [{"role": "user", "content": user_content}]
        })

        logger.info(f"Completed {agent_type} agent")
        return result["messages"][-1].content
    except Exception as e:
        logger.error(f"Error in {agent_type} agent: {str(e)}")
        return f"Analysis failed for {agent_type}: {str(e)}"

async def tape_study_agent(card: Card, model_override: Optional[str] = None, use_serper: bool = False, api_keys: Optional[Dict[str, str]] = None, custom_prompt: Optional[str] = None) -> str:
    logger.info(f"Starting tape_study agent (serper: {use_serper})")
    try:
        model_name = model_override if model_override else get_model_for_agent("tape_study")
        system_prompt = custom_prompt if custom_prompt else TAPE_STUDY_PROMPT
   

        # Determine tools based on use_serper flag
        tools = [serper_search] if use_serper else []

        # Create agent with conditional tools
        agent = create_agent(
            model=model_name,
            tools=tools,
            response_format=None,  # Text response
            system_prompt=system_prompt
        )

        if use_serper:
            user_content = f"Analyze this UFC card technical analysis:\n{card}\n\nYou can use the serper_search tool to find recent fight footage analysis, technical breakdowns, and expert commentary about fighters."
        else:
            user_content = f"Analyze this UFC card technical analysis:\n{card}"

        result = agent.invoke({
            "messages": [{"role": "user", "content": user_content}]
        })

        logger.info(f"Completed tape_study agent (serper: {use_serper})")
        return result["messages"][-1].content
    except Exception as e:
        logger.error(f"Error in tape_study agent: {str(e)}")
        return f"Analysis failed for tape_study: {str(e)}"

async def stats_trends_agent(card: Card, model_override: Optional[str] = None, use_serper: bool = False, api_keys: Optional[Dict[str, str]] = None, custom_prompt: Optional[str] = None) -> str:
    logger.info(f"Starting stats_trends agent (serper: {use_serper})")
    try:
        model_name = model_override if model_override else get_model_for_agent("stats_trends")
        system_prompt = custom_prompt if custom_prompt else STATS_TRENDS_PROMPT


        # Determine tools based on use_serper flag
        tools = [serper_search] if use_serper else []

        # Create agent with conditional tools
        agent = create_agent(
            model=model_name,
            tools=tools,
            response_format=None,  # Text response
            system_prompt=system_prompt
        )

        if use_serper:
            user_content = f"Analyze this UFC card statistical trends:\n{card}\n\nYou can use the serper_search tool to find recent statistical data, performance trends, and fighter statistics updates."
        else:
            user_content = f"Analyze this UFC card statistical trends:\n{card}"

        result = agent.invoke({
            "messages": [{"role": "user", "content": user_content}]
        })

        logger.info(f"Completed stats_trends agent (serper: {use_serper})")
        return result["messages"][-1].content
    except Exception as e:
        logger.error(f"Error in stats_trends agent: {str(e)}")
        return f"Analysis failed for stats_trends: {str(e)}"

async def news_weighins_agent(card: Card, model_override: Optional[str] = None, use_serper: bool = False, api_keys: Optional[Dict[str, str]] = None, custom_prompt: Optional[str] = None) -> str:
    logger.info(f"Starting news_weighins agent (serper: {use_serper})")
    try:
        model_name = model_override if model_override else get_model_for_agent("news_weighins")
        system_prompt = custom_prompt if custom_prompt else NEWS_WEIGHINS_PROMPT
   

        if model_name.startswith("gemini"):
            logger.info(f"Starting news_weighins agent with Gemini: {model_name}")
            # Use direct Gemini API with GoogleSearch
            api_key = get_api_key("google", api_keys)
            client = genai.Client(api_key=api_key)
            prompt = f"""{system_prompt}

Analyze this UFC card for news and external factors:
{card}

Use the Google Search tool to find recent news about fighters, injuries, weigh-in reports, and training camp updates."""

            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=GenerateContentConfig(
                    tools=[Tool(google_search=GoogleSearch())]
                )
            )
            logger.info(f"Completed news_weighins agent with Gemini")
            return response.text
        else:
            # Use LangChain approach with optional Serper
            # Determine tools based on use_serper flag
            tools = [serper_search] if use_serper else []

            # Create agent with conditional tools
            agent = create_agent(
                model=model_name,
                tools=tools,
                response_format=None,  # Text response
                system_prompt=system_prompt
            )

            if use_serper:
                user_content = f"Analyze this UFC card for news and external factors:\n{card}\n\nYou can use the serper_search tool to find recent news about fighters, injuries, weigh-in reports, and training camp updates."
            else:
                user_content = f"Analyze this UFC card for news and external factors:\n{card}"

            result = agent.invoke({
                "messages": [{"role": "user", "content": user_content}]
            })

            logger.info(f"Completed news_weighins agent (serper: {use_serper})")
            return result["messages"][-1].content
    except Exception as e:
        logger.error(f"Error in news_weighins agent: {str(e)}")
        return f"Analysis failed for news_weighins: {str(e)}"

async def style_matchup_agent(card: Card, model_override: Optional[str] = None, use_serper: bool = False, api_keys: Optional[Dict[str, str]] = None, custom_prompt: Optional[str] = None) -> str:
    logger.info(f"Starting style_matchup agent (serper: {use_serper})")
    try:
        model_name = model_override if model_override else get_model_for_agent("style_matchup")
        system_prompt = custom_prompt if custom_prompt else STYLE_MATCHUP_PROMPT
      

        # Determine tools based on use_serper flag
        tools = [serper_search] if use_serper else []

        # Create agent with conditional tools
        agent = create_agent(
            model=model_name,
            tools=tools,
            response_format=None,  # Text response
            system_prompt=system_prompt
        )

        if use_serper:
            user_content = f"Analyze this UFC card fighting styles and matchup dynamics:\n{card}\n\nYou can use the serper_search tool to find recent fighter style analysis, matchup predictions, and expert commentary."
        else:
            user_content = f"Analyze this UFC card fighting styles and matchup dynamics:\n{card}"

        result = agent.invoke({
            "messages": [{"role": "user", "content": user_content}]
        })

        logger.info(f"Completed style_matchup agent (serper: {use_serper})")
        return result["messages"][-1].content
    except Exception as e:
        logger.error(f"Error in style_matchup agent: {str(e)}")
        return f"Analysis failed for style_matchup: {str(e)}"

async def market_odds_agent(card: Card, model_override: Optional[str] = None, use_serper: bool = False, api_keys: Optional[Dict[str, str]] = None, custom_prompt: Optional[str] = None) -> str:
    logger.info(f"Starting market_odds agent (serper: {use_serper})")
    try:
        model_name = model_override if model_override else get_model_for_agent("market_odds")
        system_prompt = custom_prompt if custom_prompt else MARKET_ODDS_PROMPT

        # Determine tools based on use_serper flag
        tools = [serper_search] if use_serper else []

        # Create agent with conditional tools
        agent = create_agent(
            model=model_name,
            tools=tools,
            response_format=None,  # Text response
            system_prompt=system_prompt
        )

        if use_serper:
            user_content = f"Analyze this UFC card betting odds and market movements:\n{card}\n\nYou can use the serper_search tool to find current odds data, line movements, and market analysis."
        else:
            user_content = f"Analyze this UFC card betting odds and market movements:\n{card}"

        result = agent.invoke({
            "messages": [{"role": "user", "content": user_content}]
        })

        logger.info(f"Completed market_odds agent (serper: {use_serper})")
        return result["messages"][-1].content
    except Exception as e:
        logger.error(f"Error in market_odds agent: {str(e)}")
        return f"Analysis failed for market_odds: {str(e)}"

async def judge_agent(card: Card, tape: str, stats: str, news: str, style: str, market: str, model_override: Optional[str] = None, api_keys: Optional[Dict[str, str]] = None, custom_prompt: Optional[str] = None) -> List[FightAnalysis]:
    logger.info("Starting judge agent")
    try:
        model_name = model_override if model_override else get_model_for_agent("judge")

        system_prompt = custom_prompt if custom_prompt else """
You are the final judge synthesizing all analyses into a definitive prediction.

Synthesize the following analyses from different experts for each fight on the UFC card.
"""
       
        # Create agent with structured output
        agent = create_agent(
            model=model_name,
            tools=[],  # No tools for judge
            response_format=ToolStrategy(CardAnalysis),  # Structured output
            system_prompt=system_prompt
        )

        user_content = f"""
Synthesize these analyses into final predictions:

Tape Study: {tape}
Stats & Trends: {stats}
News/Weigh-ins: {news}
Style Matchup: {style}
Market/Odds: {market}

Provide final analysis for all fights with picks, confidence, path to victory, risk flags, and props.
"""

        result = agent.invoke({
            "messages": [{"role": "user", "content": user_content}]
        })

        logger.info(f"Judge agent completed with structured response")
        str_resp_analyses = result["structured_response"].analyses
        result_json = []
        for analysis in str_resp_analyses:
            result_json.append(analysis.dict())

        return result_json
    except Exception as e:
        logger.error(f"Error in judge agent: {str(e)}")
        return []

# Post agents - now using LangChain agents

async def risk_scorer_agent(analyses: List[FightAnalysis], model_override: Optional[str] = None, api_keys: Optional[Dict[str, str]] = None, custom_prompt: Optional[str] = None) -> List[FightAnalysis]:
    """Risk Scorer Agent - enhances risk flags using LLM analysis"""
    logger.info(f"Starting risk scorer agent for {len(analyses)} analyses")
    try:
        model_name = model_override if model_override else get_model_for_agent("risk_scorer")

        system_prompt = custom_prompt if custom_prompt else """
You are an expert risk assessor for UFC fights. Review the current fight analyses and identify additional risk factors that could affect outcomes.

Consider factors like:
- Fighter form and recent performance
- Injury history and recovery time
- Weight cut difficulties
- Training camp issues
- Age and experience factors
- Style matchup concerns
- Overconfidence indicators

Add relevant risk flags to each analysis while preserving existing ones.
"""
        
        agent = create_agent(
            model=model_name,
            tools=[],  # No tools needed
            response_format=ToolStrategy(CardAnalysis),  # Structured output
            system_prompt=system_prompt
        )

        # Serialize current analyses for input
        current_card = CardAnalysis(analyses=analyses)
        analyses_json = current_card.model_dump_json()

        user_content = f"""
Review these fight predictions and enhance the risk flags:

{analyses_json}

Add any additional risk factors you identify. Preserve existing risk flags and add new relevant ones.
Return the complete updated analysis with enhanced risk assessment.
"""

        result = agent.invoke({
            "messages": [{"role": "user", "content": user_content}]
        })

        logger.info("Risk scorer agent completed")
        return result["structured_response"].analyses

    except Exception as e:
        logger.error(f"Error in risk scorer agent: {str(e)}")
        # Fallback to basic risk assessment
        for analysis in analyses:
            if analysis.confidence > 90:
                analysis.risk_flags.append("high confidence may indicate overestimation")
            if len(analysis.risk_flags) == 0:
                analysis.risk_flags.append("no major risks identified")
        return analyses

async def consistency_checker_agent(analyses: List[FightAnalysis], model_override: Optional[str] = None, api_keys: Optional[Dict[str, str]] = None, custom_prompt: Optional[str] = None) -> List[FightAnalysis]:
    """Consistency Checker Agent - validates and adjusts confidence scores"""
    logger.info(f"Starting consistency checker agent for {len(analyses)} analyses")
    try:
        model_name = model_override if model_override else get_model_for_agent("consistency_checker")

        system_prompt = custom_prompt if custom_prompt else """
You are a consistency checker for UFC fight predictions. Review the analyses for logical consistency and adjust confidence scores as needed.

Consider:
- Conflicting signals between different analysis aspects
- Overconfidence in uncertain matchups
- Underestimation of upsets
- Risk factors that should reduce confidence
- Consistency with historical outcomes

Adjust confidence scores (0-100) to better reflect realistic probabilities while maintaining the pick.
"""

        agent = create_agent(
            model=model_name,
            tools=[],  # No tools needed
            response_format=ToolStrategy(CardAnalysis),  # Structured output
            system_prompt=system_prompt
        )

        # Serialize current analyses for input
        current_card = CardAnalysis(analyses=analyses)
        analyses_json = current_card.model_dump_json()

        user_content = f"""
Review these fight predictions for consistency and adjust confidence scores if needed:

{analyses_json}

Check for logical consistency and adjust confidence scores to reflect realistic probabilities.
Maintain the same picks but calibrate confidence appropriately.
"""

        result = agent.invoke({
            "messages": [{"role": "user", "content": user_content}]
        })

        logger.info("Consistency checker agent completed")
        return result["structured_response"].analyses

    except Exception as e:
        logger.error(f"Error in consistency checker agent: {str(e)}")
        # Fallback to basic consistency check
        for analysis in analyses:
            if len(analysis.risk_flags) > 1:
                analysis.confidence = max(50, analysis.confidence - 10)
        return analyses
