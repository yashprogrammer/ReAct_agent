from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from agent.bot import create_react_agent_custom
from utils.logger import get_logger
from tools.notion_calendar import get_calendar_events
from tools.notion_notes import get_notes

logger = get_logger(__name__)

app = FastAPI(title="ReAct Agent API")

# Allow CORS for development convience (though mostly serving static now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent on startup
agent = None

@app.on_event("startup")
async def startup_event():
    global agent
    try:
        agent = create_react_agent_custom()
        logger.info("Agent initialized in API")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        pass

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, Any]]] = None

@app.post("/chat")
async def chat(request: ChatRequest):
    global agent
    if not agent:
         raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        # We invoke the agent with the user's message.
        # Ideally, we should convert the 'history' to LangChain messages to maintain context,
        # but for now, we'll stick to the basic single-turn or implicit history if the agent manages it.
        # The ReAct agent typically needs the chat history passed in if we want it to remember previous turns unless using a persistent checkpoint.
        
        # Simple invocation
        response = agent.invoke({"messages": [("user", request.message)]})
        
        if isinstance(response, dict) and "messages" in response:
            messages = response["messages"]
            if messages:
                last_msg = messages[-1]
                return {"response": last_msg.content}
        
        return {"response": str(response)}

    except Exception as e:
        logger.error(f"Error during chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendar")
async def get_calendar(date: str = Query(...)):
    try:
        # Directly call the tool logic. 
        # Note: Tools return dicts or strings. The logic in get_calendar_events returns a dict.
        result = get_calendar_events.invoke(date)
        if isinstance(result, str) and result.startswith("Error"):
             raise HTTPException(status_code=500, detail=result)
        return result
    except Exception as e:
        logger.error(f"Error fetching calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notes")
async def get_notion_notes():
    try:
        # Directly call the tool logic.
        result = get_notes.invoke({})
        # result is expected to be a list or an error string
        if isinstance(result, str) and result.startswith("Error"):
             raise HTTPException(status_code=500, detail=result)
        return {"notes": result}
    except Exception as e:
        logger.error(f"Error fetching notes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

# Mount static files (Frontend)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
