# service
import asyncio
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

# llama
from llama_index.llms.gemini import Gemini
from llama_index.core.tools import FunctionTool, ToolMetadata
import google.generativeai as genai


# workflow
from agent.workflow import VideoAgentWorkFlow
from agent.events import UserInputEvent, FinalResponseEvent
from agent.state import AgentState
from agent.schema import Request
from core.app_state import Appstate


from chat_data import get_chat_history, save_chat_history


async def echo_tool(t: str) -> str:
    return f"Echo: {t}"

from dotenv import load_dotenv
from os import getenv

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    genai.configure(api_key=getenv("GOOGLE_API_KEY")) # Do i Need this line ???
    GEMINI_MODELS = (
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-thinking",
        "models/gemini-2.0-flash-thinking-exp-01-21",
        "models/gemini-2.0-flash-lite",
        "models/gemini-2.0-flash-lite-preview-02-05",
        "models/gemini-2.0-pro-exp-02-05",
        "models/gemini-1.5-flash",
        "models/gemini-1.5-flash-8b",
        "models/gemini-1.0-pro",
    )

    llm = Gemini(model=GEMINI_MODELS[0])
    tool = FunctionTool(
    async_fn=echo_tool,
        metadata=ToolMetadata(
            name="echo_tool",
            description="Echoes the input text back to the user"
        )
    )
    tool =[]
    app_state = Appstate()
    app_state.workflow = VideoAgentWorkFlow(
        llm=llm,
        context_tools=[tool],
        all_tools={"echo_tool": tool},
    )
    yield
    app_state.workflow = None


app = FastAPI(lifespan=lifespan)


async def run_query(user_id: str, session_id: str, query: str) -> str:
    h = get_chat_history(user_id, session_id)
    s = AgentState()
    e = UserInputEvent(user_msg=query, chat_history=h, state=s)
    wf = Appstate().workflow
    r = None
    async for ev in wf.run_stream(input=e):
        if isinstance(ev, FinalResponseEvent):
            r = ev.response
            break
    if u := await wf.store.get("chat_history"):
        save_chat_history(session_id, u)
    return r or ""


@app.post("/query", response_model=FinalResponseEvent)
async def query(req: Request):
    try:
        res = await run_query(req.user_id, req.session_id, req.query)
        return FinalResponseEvent(response=res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("service:app", host="0.0.0.0", port=8000, reload=True)


