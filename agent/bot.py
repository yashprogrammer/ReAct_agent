import os
from langchain_groq import ChatGroq
# Importing create_agent as requested. 
# Note: If this fails, it might be due to version mismatch or the notebook using a specific environmental setup.
try:
    from langchain.agents import create_agent
except ImportError:
    # Fallback or re-export check
    # In some contexts create_agent might be create_react_agent or similar, 
    # but strictly following user instruction to use create_agent.
    from langchain.agents import create_react_agent as create_agent

from tools.weather import get_weather
from tools.notion_notes import get_notes, add_note
from tools.notion_calendar import get_calendar_events, add_calendar_event
from tools.dummy import dummy_tool
from utils.logger import get_logger

logger = get_logger(__name__)

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY not found")
        raise ValueError("GROQ_API_KEY not set")
    
    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.5,
        api_key=api_key
    )

def create_react_agent_custom():
    logger.info("Initializing Agent...")
    llm = get_llm()
    
    tools = [
        get_weather,
        get_notes,
        add_note,
        get_calendar_events,
        add_calendar_event,
        dummy_tool
    ]
    
    # User requested 'create_agent' specifically.
    # The notebook usage: create_agent(model=llm_groq, tools=tools)
    try:
        agent = create_agent(model=llm, tools=tools)
        logger.info("Agent initialized successfully.")
        return agent
    except TypeError as e:
        # If create_agent signature is different (e.g. requires prompt)
        logger.error(f"Failed to create agent with create_agent: {e}")
        raise e
