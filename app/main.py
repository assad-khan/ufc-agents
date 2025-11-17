from fastapi import FastAPI, HTTPException
from app.models import Card, CardAnalysis
from app.agents import (
    tape_study_agent, stats_trends_agent, news_weighins_agent,
    style_matchup_agent, market_odds_agent, judge_agent,
    risk_scorer_agent, consistency_checker_agent
)
import asyncio
from loguru import logger

app = FastAPI(title="UFC Card Analysis API", version="1.0.0")

@app.post("/analyze-card", response_model=CardAnalysis)
async def analyze_card(card: Card):
    try:
        logger.info(f"Analyzing card with {len(card.fights)} fights")

        # Extract model overrides from card
        agent_models = card.agent_models

        # # Run 5 main agents in parallel
        tape_task = tape_study_agent(card, agent_models.tape_study if agent_models else None, card.use_serper)
        stats_task = stats_trends_agent(card, agent_models.stats_trends if agent_models else None, card.use_serper)
        news_task = news_weighins_agent(card, agent_models.news_weighins if agent_models else None, card.use_serper)
        style_task = style_matchup_agent(card, agent_models.style_matchup if agent_models else None, card.use_serper)
        market_task = market_odds_agent(card, agent_models.market_odds if agent_models else None, card.use_serper)

        tape, stats, news, style, market = await asyncio.gather(
            tape_task, stats_task, news_task, style_task, market_task
        )

        logger.info("Main agents completed")

        # Judge agent
        analyses = await judge_agent(card, tape, stats, news, style, market, agent_models.judge if agent_models else None)
        logger.info("Judge completed")
        # Post agents
        analyses = await risk_scorer_agent(analyses, agent_models.risk_scorer if agent_models else None)
        analyses = await consistency_checker_agent(analyses, agent_models.consistency_checker if agent_models else None)

        logger.info("Post agents completed")

        return CardAnalysis(analyses=analyses)

    except Exception as e:
        logger.error(f"Error analyzing card: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "UFC Card Analysis API", "endpoint": "/analyze-card"}
