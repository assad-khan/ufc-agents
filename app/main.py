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

        # Run 5 main agents in parallel
        tape_task = tape_study_agent(card)
        stats_task = stats_trends_agent(card)
        news_task = news_weighins_agent(card)
        style_task = style_matchup_agent(card)
        market_task = market_odds_agent(card)

        tape, stats, news, style, market = await asyncio.gather(
            tape_task, stats_task, news_task, style_task, market_task
        )

        logger.info("Main agents completed")

        # Judge agent
        analyses = await judge_agent(card, tape, stats, news, style, market)
        logger.info("Judge completed")

        # Post agents
        analyses = await risk_scorer_agent(analyses)
        analyses = await consistency_checker_agent(analyses)

        logger.info("Post agents completed")

        return CardAnalysis(analyses=analyses)

    except Exception as e:
        logger.error(f"Error analyzing card: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "UFC Card Analysis API", "endpoint": "/analyze-card"}
