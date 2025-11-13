from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from app.config import get_model_for_agent
from app.models import FightAnalysis, Card, CardAnalysis
from typing import List, Dict, Any
import asyncio
from loguru import logger

# No longer need output parsers - using ToolStrategy for structured output

# System prompts for analysis agents
TAPE_STUDY_PROMPT = """
You are a UFC tape study expert analyzing fight footage and past performances.
Focus on fighter tendencies, striking patterns, grappling weaknesses, and recent performance.
Provide detailed insights for each fight including technical advantages and potential fight-ending sequences.
"""

STATS_TRENDS_PROMPT = """
You are a UFC statistics and trends analyst.
Analyze using statistical data and historical trends including win/loss records, striking accuracy, takedown defense, and finish rates.
Provide statistical comparisons and trend analysis for each fight.
"""

NEWS_WEIGHINS_PROMPT = """
You are a UFC news and weigh-ins analyst.
Analyze recent news, weigh-in reports, and external factors including injuries, training camp reports, and press conferences.
Provide insights on how external factors might affect each fight.
"""

STYLE_MATCHUP_PROMPT = """
You are a UFC style matchup analyst.
Analyze fighting styles and matchup dynamics considering stand-up vs ground game, pace, durability, and experience levels.
Provide style advantage analysis and matchup predictions for each fight.
"""

MARKET_ODDS_PROMPT = """
You are a UFC market and odds analyst.
Analyze betting odds and market movements considering line movements, public money, and sharp money.
Provide odds analysis and value picks for each fight.
"""

JUDGE_PROMPT = """
You are the final judge synthesizing all analyses into a definitive prediction.

Synthesize the following analyses from different experts for each fight on the UFC card:

Tape Study: {tape_analysis}
Stats & Trends: {stats_analysis}
News/Weigh-ins: {news_analysis}
Style Matchup: {style_analysis}
Market/Odds: {market_analysis}

Provide a final analysis for all fights in the following JSON format:
{format_instructions}

Ensure each analysis has the correct fight_id, pick is one of the fighter names, confidence is 0-100.
"""

RISK_SCORER_PROMPT = """
You are a risk assessment expert for UFC fights.

Review the following judge analyses and identify additional risk factors:

{judge_analyses}

For each fight, add risk flags such as:
- Injury concerns
- Weight cut issues
- Long layoff
- Style mismatch
- Age/experience factors

Return updated analyses with risk_flags added.
"""

CONSISTENCY_CHECKER_PROMPT = """
You are a consistency checker for UFC predictions.

Review the following analyses for logical consistency and adjust confidence scores if needed:

{risk_analyses}

Check for:
- Conflicting signals
- Overconfidence in uncertain matchups
- Underestimation of upsets

Return final analyses with adjusted confidence scores and consistency notes.
"""

async def run_agent(agent_type: str, system_prompt: str, card: Card) -> str:
    logger.info(f"Starting {agent_type} agent for {len(card.fights)} fights")
    try:
        model_name = get_model_for_agent(agent_type)

        card_info = "\n".join([
            f"Fight {f.fight_id}: {f.fighter1} vs {f.fighter2} ({f.weight_class})"
            for f in card.fights
        ])

        # Create agent using the new API
        agent = create_agent(
            model=model_name,
            tools=[],  # No tools for analysis agents
            response_format=None,  # Text response
            system_prompt=system_prompt
        )

        user_content = f"Analyze this UFC card:\n{card_info}"
        result = agent.invoke({
            "messages": [{"role": "user", "content": user_content}]
        })

        logger.info(f"Completed {agent_type} agent")
        # Handle different response formats
        # if "response" in result:
        #     return result["response"]
        # elif hasattr(result, 'messages') and result.messages:
        #     return result.messages[-1].content
        # elif "output" in result:
        #     return result["output"]
        # else:
        #     # Fallback: return the result as string
        #     return str(result)
        return result["messages"][-1].content
    except Exception as e:
        logger.error(f"Error in {agent_type} agent: {str(e)}")
        return f"Analysis failed for {agent_type}: {str(e)}"

async def tape_study_agent(card: Card) -> str:
    return await run_agent("tape_study", TAPE_STUDY_PROMPT, card)

async def stats_trends_agent(card: Card) -> str:
    return await run_agent("stats_trends", STATS_TRENDS_PROMPT, card)

async def news_weighins_agent(card: Card) -> str:
    return await run_agent("news_weighins", NEWS_WEIGHINS_PROMPT, card)

async def style_matchup_agent(card: Card) -> str:
    return await run_agent("style_matchup", STYLE_MATCHUP_PROMPT, card)

async def market_odds_agent(card: Card) -> str:
    return await run_agent("market_odds", MARKET_ODDS_PROMPT, card)

async def judge_agent(card: Card, tape: str, stats: str, news: str, style: str, market: str) -> List[FightAnalysis]:
    logger.info("Starting judge agent")
    try:
        model_name = get_model_for_agent("judge")

        system_prompt = """
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

async def risk_scorer_agent(analyses: List[FightAnalysis]) -> List[FightAnalysis]:
    """Risk Scorer Agent - enhances risk flags using LLM analysis"""
    logger.info(f"Starting risk scorer agent for {len(analyses)} analyses")
    try:
        model_name = get_model_for_agent("risk_scorer")

        system_prompt = """
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

async def consistency_checker_agent(analyses: List[FightAnalysis]) -> List[FightAnalysis]:
    """Consistency Checker Agent - validates and adjusts confidence scores"""
    logger.info(f"Starting consistency checker agent for {len(analyses)} analyses")
    try:
        model_name = get_model_for_agent("consistency_checker")

        system_prompt = """
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
