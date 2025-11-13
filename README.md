# UFC Card Analysis API

A FastAPI application that analyzes UFC fight cards using multiple LangChain-powered LLM agents running in parallel.

## Features

- **Parallel Agent Analysis**: 5 specialized agents analyze UFC cards concurrently
  - Tape Study (claude-3-7-sonnet-20250219)
  - Stats & Trends (claude-3-7-sonnet-20250219)
  - News/Weigh-ins (GPT-4o)
  - Style Matchup (claude-3-7-sonnet-20250219)
  - Market/Odds (GPT-4o)
- **Judge Agent**: Synthesizes all analyses into structured JSON predictions
- **Post-Processing**: Risk Scorer and Consistency Checker refine results
- **Configurable Models**: Mix OpenAI, Anthropic, and Google models for optimal precision

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your keys
   ```

## Running the API

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Usage

### POST /analyze-card

Analyzes a UFC card and returns predictions for each fight.

**Request Body:**
```json
{
  "fights": [
    {
      "fight_id": "main_event",
      "fighter1": "Alex Pereira",
      "fighter2": "Jared Cannonier",
      "weight_class": "Middleweight",
      "fighter1_record": "7-1",
      "fighter2_record": "16-6"
    }
  ]
}
```

**Response:**
```json
{
  "analyses": [
    {
      "fight_id": "main_event",
      "pick": "Alex Pereira",
      "confidence": 85,
      "path_to_victory": "KO in round 2 via head kick",
      "risk_flags": ["recent injury"],
      "props": ["over 2.5 rounds"]
    }
  ]
}
```

## Agent Model Assignments

- **Tape Study**: claude-3-7-sonnet-20250219 
- **Stats & Trends**: claude-3-7-sonnet-20250219
- **News/Weigh-ins**: GPT-4o 
- **Style Matchup**: claude-3-7-sonnet-20250219
- **Market/Odds**: GPT-4o 
- **Judge**: GPT-4o 
- **Risk Scorer**: claude-3-7-sonnet-20250219
- **Consistency Checker**: GPT-4o 

## Architecture

The system uses LangChain for agent orchestration with specialized prompts for each analysis type. Agents run asynchronously for maximum performance, with structured output parsing ensuring consistent JSON responses.
