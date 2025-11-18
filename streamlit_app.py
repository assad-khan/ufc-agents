import streamlit as st
import requests
import json
from typing import List, Dict, Any
import csv
import io
import time
import asyncio
from datetime import datetime

# Direct UFC analysis imports
from app.models import Card, CardAnalysis
from app.agents import (
    tape_study_agent, stats_trends_agent, news_weighins_agent,
    style_matchup_agent, market_odds_agent, judge_agent,
    risk_scorer_agent, consistency_checker_agent
)
from app.config import set_runtime_api_keys

# Page configuration
st.set_page_config(
    page_title="🥊 UFC Card Analysis Expert",
    page_icon="🥊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UFC theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #dc2626 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    .fight-card {
        background: linear-gradient(135deg, #111827, #1f2937);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #374151;
    }
    .fighter-name {
        font-size: 1.2rem;
        font-weight: bold;
        color: #10b981;
    }
    .confidence-bar {
        height: 20px;
        background: #374151;
        border-radius: 10px;
        overflow: hidden;
    }
    .confidence-fill {
        height: 100%;
        transition: width 1s ease-in-out;
    }
    .high-confidence { background: linear-gradient(90deg, #dc2626, #ea580c); }
    .medium-confidence { background: linear-gradient(90deg, #ea580c, #f59e0b); }
    .low-confidence { background: linear-gradient(90deg, #f59e0b, #10b981); }
    .risk-flag {
        background: #dc2626;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.25rem 0;
        font-size: 0.9rem;
    }
    .prop-bet {
        background: #1e3a8a;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.25rem 0;
        font-size: 0.9rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #dc2626, #ea580c);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
    }
    .analysis-result {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #1e40af;
    }
    .sidebar-fight {
        background: #111827;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #374151;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🥊 UFC Card Analysis Expert</h1>', unsafe_allow_html=True)
st.markdown("""
**Enterprise-Grade MMA Intelligence Platform**

This tool leverages advanced AI agents to provide comprehensive UFC fight card analysis,
combining technical expertise, statistical modeling, and real-time intelligence.
""")

# Initialize api_keys as None
api_keys = None
# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Analysis Configuration")

    # Web search toggle (must be defined before API key validation)
    use_serper = st.toggle("🔍 Enable Real-Time Web Search", help="Uses Serper API for live news, injuries, and fighter updates", key="use_serper_toggle")

    # API keys input section
    st.markdown("🔐 API Keys Configuration")
    with st.expander("🔑 Enter API Keys"):
        st.markdown("**Required for analysis:**")
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            key="openai_key_input",
            help="Your OpenAI API key (e.g., sk-proj-...)"
        )
        anthropic_key = st.text_input(
            "Anthropic API Key",
            type="password",
            key="anthropic_key_input",
            help="Your Claude/Anthropic API key (e.g., sk-ant-api03-...)"
        )
        serper_key = st.text_input(
            "Serper API Key",
            type="password",
            key="serper_key_input",
            help="Your Serper web search API key (only needed when web search is enabled)"
        )

        # Validate required API keys (Serper only when web search enabled)
        api_key_validation_errors = []
        if not openai_key.strip():
            api_key_validation_errors.append("OpenAI API Key is required")
        if not anthropic_key.strip():
            api_key_validation_errors.append("Anthropic API Key is required")
        if use_serper and not serper_key.strip():
            api_key_validation_errors.append("Serper API Key is required (for Web Search)")

        if api_key_validation_errors:
            for error in api_key_validation_errors:
                st.error(error)
            api_keys = None
        else:
            # Only include Serper key if web search is enabled
            api_keys = {
                "openai": openai_key.strip(),
                "anthropic": anthropic_key.strip()
            }
            if use_serper:
                api_keys["serper"] = serper_key.strip()
            st.success(f"✅ All API keys configured ({len(api_keys)} keys)")

    # Advanced settings
    with st.expander("🔧 Advanced Settings"):
        st.markdown("**Agent Model Overrides** (Optional)")

        agent_models = {}

        col1, col2 = st.columns(2)

        with col1:
            agent_models['tape_study'] = st.selectbox(
                "Tape Study Agent",
                ["claude-3-7-sonnet-20250219", "claude-3-5-sonnet", "gpt-5", "gpt-4"],
                help="Technical combat analysis expert"
            )
            agent_models['stats_trends'] = st.selectbox(
                "Stats & Trends Agent",
                ["gpt-5", "gpt-4", "claude-3-7-sonnet-20250219"],
                help="Quantitative performance analyst"
            )
            agent_models['news_weighins'] = st.selectbox(
                "News & Intelligence Agent",
                ["gpt-5", "gpt-4", "claude-3-7-sonnet-20250219"],
                help="External factors specialist"
            )
            agent_models['style_matchup'] = st.selectbox(
                "Style Matchup Agent",
                ["claude-3-7-sonnet-20250219", "claude-3-5-sonnet", "gpt-5"],
                help="Fighting style compatibility expert"
            )

        with col2:
            agent_models['market_odds'] = st.selectbox(
                "Market & Odds Agent",
                ["gpt-5-mini", "gpt-4", "gpt-3.5"],
                help="Betting market analyst"
            )
            agent_models['judge'] = st.selectbox(
                "Judge Agent",
                ["gpt-5", "gpt-4", "claude-3-7-sonnet-20250219"],
                help="Multi-disciplinary synthesis"
            )
            agent_models['risk_scorer'] = st.selectbox(
                "Risk Scorer",
                ["gpt-5-mini", "gpt-4", "claude-3-5-haiku"],
                help="Uncertainty assessment"
            )
            agent_models['consistency_checker'] = st.selectbox(
                "Consistency Checker",
                ["claude-3-5-haiku-20241022", "gpt-4", "claude-3-5-sonnet"],
                help="Quality assurance"
            )


def create_fight_form(fight_num: int) -> Dict[str, Any]:
    """Create a form section for a single fight"""
    st.markdown('<div class="sidebar-fight">', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("🗑️", key=f"remove_fight_{fight_num}"):
            # Decrement session state counter
            if 'fight_count' in st.session_state and st.session_state.fight_count > 1:
                st.session_state.fight_count -= 1
            st.rerun()

    with col2:
        st.markdown(f"**Fight #{fight_num}**")

    # Fight details
    col1, col2 = st.columns(2)

    with col1:
        fighter1 = st.text_input(
            f"Red Corner #{fight_num}",
            key=f"fighter1_{fight_num}",
            placeholder="e.g., Alexander Volkanovski"
        )
        fighter1_record = st.text_input(
            "Record",
            key=f"fighter1_record_{fight_num}",
            placeholder="e.g., 25-3-0"
        )

    with col2:
        fighter2 = st.text_input(
            f"Blue Corner #{fight_num}",
            key=f"fighter2_{fight_num}",
            placeholder="e.g., Ilia Topuria"
        )
        fighter2_record = st.text_input(
            "Record",
            key=f"fighter2_record_{fight_num}",
            placeholder="e.g., 14-0-0"
        )

    # Additional info
    weight_class = st.selectbox(
        "Weight Class",
        ["Strawweight", "Flyweight", "Bantamweight", "Featherweight", "Lightweight",
         "Welterweight", "Middleweight", "Light Heavyweight", "Heavyweight"],
        key=f"weight_class_{fight_num}"
    )

    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Fight Date", key=f"date_{fight_num}")
    with col2:
        location = st.text_input(
            "Location",
            key=f"location_{fight_num}",
            placeholder="e.g., Etihad Arena, Abu Dhabi"
        )

    additional_info = st.text_area(
        "Additional Info",
        key=f"additional_info_{fight_num}",
        placeholder="e.g., UFC Featherweight Championship",
        height=68
    )

    st.markdown('</div>', unsafe_allow_html=True)

    return {
        "fight_id": f"fight_{fight_num}",
        "fighter1": fighter1,
        "fighter2": fighter2,
        "weight_class": weight_class,
        "fighter1_record": fighter1_record,
        "fighter2_record": fighter2_record,
        "date": date.isoformat() if date else None,
        "location": location,
        "additional_info": additional_info
    }

def validate_fight(fight_data: Dict[str, Any]) -> List[str]:
    """Validate fight data and return list of errors"""
    errors = []

    if not fight_data.get("fighter1"):
        errors.append("Red Corner fighter name is required")
    if not fight_data.get("fighter2"):
        errors.append("Blue Corner fighter name is required")
    if fight_data.get("fighter1") == fight_data.get("fighter2"):
        errors.append("Fighters cannot be the same person")

    return errors

# Extract and modify analyze_card function for direct usage
async def analyze_card_direct(card: Card):
    """Direct analysis function (extracted from app/main.py)"""
    try:
        # Extract model overrides and API keys from card
        agent_models = card.agent_models
        api_keys = card.api_keys

        # Set runtime API keys to environment if provided
        set_runtime_api_keys(api_keys)

        # Run 5 main agents in parallel
        tape_task = tape_study_agent(card, agent_models.tape_study if agent_models else None, card.use_serper, api_keys)
        stats_task = stats_trends_agent(card, agent_models.stats_trends if agent_models else None, card.use_serper, api_keys)
        news_task = news_weighins_agent(card, agent_models.news_weighins if agent_models else None, card.use_serper, api_keys)
        style_task = style_matchup_agent(card, agent_models.style_matchup if agent_models else None, card.use_serper, api_keys)
        market_task = market_odds_agent(card, agent_models.market_odds if agent_models else None, card.use_serper, api_keys)

        tape, stats, news, style, market = await asyncio.gather(
            tape_task, stats_task, news_task, style_task, market_task
        )

        # Judge agent
        analyses = await judge_agent(card, tape, stats, news, style, market, agent_models.judge if agent_models else None, api_keys)

        # Post agents
        analyses = await risk_scorer_agent(analyses, agent_models.risk_scorer if agent_models else None, api_keys)
        analyses = await consistency_checker_agent(analyses, agent_models.consistency_checker if agent_models else None, api_keys)

        return CardAnalysis(analyses=analyses)

    except Exception as e:
        raise Exception(f"Analysis failed: {str(e)}")

def run_direct_analysis(fights_data: List[Dict[str, Any]], use_serper: bool, agent_models: Dict[str, str], api_keys: Dict[str, str] = None):
    """Run analysis directly without HTTP requests"""
    # Convert fights data to Card model
    card = Card(
        fights=fights_data,
        use_serper=use_serper,
        agent_models=agent_models,
        api_keys=api_keys
    )

    # Run analysis in new event loop
    try:
        # Create new event loop for async execution
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(analyze_card_direct(card))
        loop.close()
        return result
    except Exception as e:
        raise Exception(f"Analysis failed: {str(e)}")

def display_analysis_results(results: Dict[str, Any]):
    """Display the analysis results in a beautiful format"""
    if not results or 'analyses' not in results:
        st.error("No analysis results received")
        return

    analyses = results['analyses']

    st.markdown("---")
    st.markdown("## 📊 Analysis Results")

    for i, analysis in enumerate(analyses):
        fight_id = analysis['fight_id']
        pick = analysis['pick']
        confidence = analysis['confidence']
        path_to_victory = analysis['path_to_victory']
        risk_flags = analysis['risk_flags']
        props = analysis['props']

        # Determine confidence color class
        if confidence >= 70:
            color_class = "high-confidence"
        elif confidence >= 50:
            color_class = "medium-confidence"
        else:
            color_class = "low-confidence"

        st.markdown('<div class="analysis-result">', unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"## 🥊 {fight_id} Prediction")
            st.markdown(f"**Pick: {pick}**")
            st.markdown(f"**Victory Path:** {path_to_victory}")

            # Confidence meter
            st.markdown("**Confidence Level**")
            st.markdown(f'<div class="confidence-bar"><div class="confidence-fill {color_class}" style="width: {confidence}%"></div></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align: center; margin-bottom: 1rem;">{confidence}%</div>', unsafe_allow_html=True)

            # Risk flags
            if risk_flags and isinstance(risk_flags, list) and len(risk_flags) > 0 and risk_flags[0] != "{flag}":
                st.markdown("### ⚠️ Risk Flags")
                for flag in risk_flags:
                    if isinstance(flag, str) and flag != "{flag}":
                        st.markdown(f'<div class="risk-flag">⚠️ {flag}</div>', unsafe_allow_html=True)

            # Props
            if props and isinstance(props, list) and len(props) > 0 and props[0] != "{prop}":
                st.markdown("### 🎲 Recommended Props")
                for prop in props:
                    if isinstance(prop, str) and prop != "{prop}":
                        st.markdown(f'<div class="prop-bet">🎲 {prop}</div>', unsafe_allow_html=True)

        with col2:
            # Victory visualization (simple pie chart)
            st.markdown("### 📈 Odds & Analysis")
            st.markdown("**Agent Confidence Breakdown**")
            # This could be expanded to show per-agent analysis

        st.markdown('</div>', unsafe_allow_html=True)

def create_export_buttons(results: Dict[str, Any]):
    """Create export buttons that persist across page reloads"""
    if not results or 'analyses' not in results:
        return

    st.markdown("### Export Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="📄 Export as JSON",
            data=json.dumps(results, indent=2),
            file_name="ufc_analysis.json",
            mime="application/json",
            key=f"json_download_{int(time.time())}_{id(results)}"
        )

    with col2:
        # Convert to CSV-friendly format using pure Python
        analyses = results['analyses']
        csv_output = io.StringIO()
        fieldnames = ["Fight_ID", "Pick", "Confidence", "Path_to_Victory", "Risk_Flags", "Props"]
        writer = csv.DictWriter(csv_output, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write data rows
        for analysis in analyses:
            writer.writerow({
                "Fight_ID": analysis["fight_id"],
                "Pick": analysis["pick"],
                "Confidence": analysis["confidence"],
                "Path_to_Victory": analysis["path_to_victory"],
                "Risk_Flags": "; ".join(analysis["risk_flags"]) if analysis.get("risk_flags") else "",
                "Props": "; ".join(analysis["props"]) if analysis.get("props") else ""
            })

        csv_string = csv_output.getvalue()

        st.download_button(
            label="📊 Export as CSV",
            data=csv_string,
            file_name="ufc_analysis.csv",
            mime="text/csv",
            key=f"csv_download_{int(time.time())}_{id(results)}"
        )

# Main form
st.markdown("## 🥋 Fight Card Input")

# Initialize session state for fights
if 'fight_count' not in st.session_state:
    st.session_state.fight_count = 1

# Add fight button
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown(f"**Managing {st.session_state.fight_count} fights**")
with col2:
    if st.button("➕ Add Fight") and st.session_state.fight_count < 10:
        st.session_state.fight_count += 1
        st.rerun()

# Create fight forms
fights_data = []
all_valid = True
validation_errors = []

for i in range(1, st.session_state.fight_count + 1):
    fight_data = create_fight_form(i)
    fights_data.append(fight_data)

    # Validate each fight
    errors = validate_fight(fight_data)
    if errors:
        all_valid = False
        validation_errors.extend([f"Fight #{i}: {error}" for error in errors])

# Always display results if they exist in session state
if 'analysis_results' in st.session_state and st.session_state.analysis_results:
    display_analysis_results(st.session_state.analysis_results)
    create_export_buttons(st.session_state.analysis_results)

# Analysis button and validation
analysis_blocked = False
if not api_keys:
    st.error("⚠️ **API Keys Required:** Please enter all required API keys in the sidebar before analyzing.")
    analysis_blocked = True

if validation_errors:
    st.error("Please fix the following errors before analyzing:")
    for error in validation_errors:
        st.write(f"- {error}")
    analysis_blocked = True

if not analysis_blocked:
    if st.button("🔥 Analyze Fight Card", type="primary"):
        with st.spinner("🤖 AI Agents analyzing fight card... This may take several minutes."):

            try:
                # Run direct analysis (no HTTP request)
                card_analysis = run_direct_analysis(fights_data, use_serper, agent_models, api_keys)

                # Convert CardAnalysis to expected dict format with fighter info
                analyses_with_fighters = []
                for analysis in card_analysis.analyses:
                    analysis_dict = analysis.dict()
                    # Find corresponding fight data to merge fighter names
                    # The fights_data contains the original form input
                    for fight_dict in fights_data:
                        if str(fight_dict['fight_id']) == str(analysis.fight_id):
                            analysis_dict['fighter1'] = fight_dict.get('fighter1', 'Unknown Fighter')
                            analysis_dict['fighter2'] = fight_dict.get('fighter2', 'Unknown Fighter')
                            break
                    analyses_with_fighters.append(analysis_dict)

                results = {
                    "analyses": analyses_with_fighters
                }

                st.success("Analysis complete! 🎉")

                # Store results in session state for persistence
                st.session_state.analysis_results = results

                # Display results
                display_analysis_results(results)
                create_export_buttons(results)

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
**Built with Enterprise-Grade MMA Intelligence:**  
Tape Study • Statistical Modeling • Real-Time Intelligence • Behavioral Analysis
""")
