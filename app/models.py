from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class AgentTemperatures(BaseModel):
    """Custom temperature settings for specific agents"""
    tape_study: Optional[float] = Field(default=None, description="Temperature (0.0-1.0) for tape study agent")
    stats_trends: Optional[float] = Field(default=None, description="Temperature (0.0-1.0) for stats & trends agent")
    news_weighins: Optional[float] = Field(default=None, description="Temperature (0.0-1.0) for news & intelligence agent")
    style_matchup: Optional[float] = Field(default=None, description="Temperature (0.0-1.0) for style matchup agent")
    market_odds: Optional[float] = Field(default=None, description="Temperature (0.0-1.0) for market & odds agent")
    judge: Optional[float] = Field(default=None, description="Temperature (0.0-1.0) for judge agent")
    risk_scorer: Optional[float] = Field(default=None, description="Temperature (0.0-1.0) for risk scorer agent")
    consistency_checker: Optional[float] = Field(default=None, description="Temperature (0.0-1.0) for consistency checker agent")

class AgentTopPs(BaseModel):
    """Custom top-p settings for specific agents"""
    tape_study: Optional[float] = Field(default=None, description="Top-p (0.0-1.0) for tape study agent")
    stats_trends: Optional[float] = Field(default=None, description="Top-p (0.0-1.0) for stats & trends agent")
    news_weighins: Optional[float] = Field(default=None, description="Top-p (0.0-1.0) for news & intelligence agent")
    style_matchup: Optional[float] = Field(default=None, description="Top-p (0.0-1.0) for style matchup agent")
    market_odds: Optional[float] = Field(default=None, description="Top-p (0.0-1.0) for market & odds agent")
    judge: Optional[float] = Field(default=None, description="Top-p (0.0-1.0) for judge agent")
    risk_scorer: Optional[float] = Field(default=None, description="Top-p (0.0-1.0) for risk scorer agent")
    consistency_checker: Optional[float] = Field(default=None, description="Top-p (0.0-1.0) for consistency checker agent")

class AgentPrompts(BaseModel):
    """Custom prompts for specific agents"""
    tape_study: Optional[str] = Field(default=None, example="Custom tape study prompt...")
    stats_trends: Optional[str] = Field(default=None, example="Custom stats prompt...")
    news_weighins: Optional[str] = Field(default=None, example="Custom news prompt...")
    style_matchup: Optional[str] = Field(default=None, example="Custom style matchup prompt...")
    market_odds: Optional[str] = Field(default=None, example="Custom market odds prompt...")
    judge: Optional[str] = Field(default=None, example="Custom judge prompt...")
    risk_scorer: Optional[str] = Field(default=None, example="Custom risk scorer prompt...")
    consistency_checker: Optional[str] = Field(default=None, example="Custom consistency checker prompt...")

class AgentModels(BaseModel):
    """Model overrides for specific agents"""
    tape_study: Optional[str] = Field(default=None, example="claude-3-7-sonnet-20250219")
    stats_trends: Optional[str] = Field(default=None, example="gpt-5")
    news_weighins: Optional[str] = Field(default=None, example="gemini-2.5-pro")
    style_matchup: Optional[str] = Field(default=None, example="claude-3-7-sonnet-20250219")
    market_odds: Optional[str] = Field(default=None, example="gpt-5-mini")
    judge: Optional[str] = Field(default=None, example="gpt-5")
    risk_scorer: Optional[str] = Field(default=None, example="gpt-5-mini")
    consistency_checker: Optional[str] = Field(default=None, example="claude-3-5-haiku-20241022")

class Fight(BaseModel):
    fight_id: str
    fighter1: str
    fighter2: str
    weight_class: str
    fighter1_record: Optional[str] = None
    fighter2_record: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    additional_info: Optional[str] = None

class Card(BaseModel):
    fights: List[Fight] = Field(
        description="List of UFC fights to analyze"
    )
    use_serper: bool = Field(
        default=False,
        description="Enable web search using Serper API for enhanced news analysis. When enabled, the news agent can search recent news, injuries, and fighter updates."
    )
    agent_models: Optional[AgentModels] = Field(
        default=None,
        description="Optional model overrides for specific agents. If not provided, defaults are used."
    )
    custom_prompts: Optional[AgentPrompts] = Field(
        default=None,
        description="Optional custom prompts for specific agents. If not provided, default prompts are used."
    )
    custom_temperatures: Optional[AgentTemperatures] = Field(
        default=None,
        description="Optional custom temperature settings for specific agents. If not provided, defaults are used."
    )
    custom_top_ps: Optional[AgentTopPs] = Field(
        default=None,
        description="Optional custom top-p settings for specific agents. If not provided, defaults are used."
    )
    api_keys: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional API keys for LLM providers. If not provided, uses environment variables. Keys: 'openai', 'anthropic', 'serper'"
    )

    class Config:
        schema_extra = {
            "example": {
                "fights": [
                    {
                        "fight_id": "ufc-fight-123",
                        "fighter1": "Alexander Volkanovski",
                        "fighter2": "Ilia Topuria",
                        "weight_class": "Featherweight",
                        "fighter1_record": "25-3-0",
                        "fighter2_record": "14-0-0",
                        "date": "2025-01-18",
                        "location": "Etihad Arena, Abu Dhabi",
                        "additional_info": "Title fight for Featherweight championship"
                    }
                ],
                "use_serper": False,
                "agent_models": {
                    "tape_study": "claude-3-7-sonnet-20250219",
                    "stats_trends": "gpt-5",
                    "news_weighins": "gpt-5",
                    "style_matchup": "claude-3-7-sonnet-20250219",
                    "market_odds": "gpt-5-mini",
                    "judge": "gpt-5",
                    "risk_scorer": "gpt-5-mini",
                    "consistency_checker": "claude-3-5-haiku-20241022"
                }
            }
        }

class FightAnalysis(BaseModel):
    fight_id: str
    pick: str
    confidence: int  # percentage 0-100
    path_to_victory: str
    risk_flags: List[str]
    props: List[str]

class CardAnalysis(BaseModel):
    analyses: List[FightAnalysis]
