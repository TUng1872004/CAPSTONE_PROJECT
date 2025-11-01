
import asyncio
from agent.workflow import VideoAgentWorkFlow
from dotenv import load_dotenv
from os import getenv

from tools.tools import single_tools
from agent.log import setup_logger, get_logger

import google.generativeai as genai
from llama_index.llms.gemini import Gemini

from agent.events import UserInputEvent, FinalResponseEvent


async def main(x =1):
    load_dotenv()
    setup_logger()
    logger = get_logger("workflow")
    genai.configure(api_key=getenv("GOOGLE_API_KEY")) 
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

    wf= VideoAgentWorkFlow(
        llm=llm,
        context_tools=[],
        all_tools=single_tools,
        logger=get_logger("Workflow")
    )
    if x ==1:
        e = UserInputEvent(input=input("Type the querry: "), chat_history=[])
        r = None
        handler = wf.run(start_event= e)
        count = 0
        async for ev in handler.stream_events(True):
            if ev: 
                print(f"Event {count}:\n {ev}")
            count+=1
            if isinstance(ev, FinalResponseEvent):
                r = ev.response
                break
    elif x ==2:
        #handler = wf.greeting_agent.run(user_msg=input("Type the querry: "), chat_history=[])
        handler = wf.greeting_agent.run(user_msg="are u gay", chat_history=[])
        print("=== HANDLER TYPE ===\n", type(handler))
        print("\n=== HANDLER DIR ===\n", dir(handler))
        
        print("Agent Finish running")
        
        async for ev in handler.stream_events():
            print(">>> EVENT:", ev)
          
        print("Agent Finish Streaming")
        
        r = handler.result()
        print("Agent return")
    return r or ""

if __name__ == "__main__":
    

    x = 1
    while(x):
        try:
            x = int(input("Make your choices: "))
            if(x == 0):
                break
            r =  asyncio.run(main(x))
            print("================== Final result ==================\n",r)
        except:
            break

            
