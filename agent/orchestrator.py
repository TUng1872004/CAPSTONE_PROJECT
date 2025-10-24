from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService, Session 
from google.genai.types import Content, Part

from google.adk.agents import Agent
import uuid


from base64 import b64decode
# Import files
from prompt import *  
from schema import *
from comms import Img, Filter
from tools import *


class Orchestrator:
    def __init__(self,DB, USER_ID: str = None, SESSION_ID : str = None, n: int = 5, APP_NAME: str = "videoQA"):
        self.app_name = APP_NAME
        self.user_id = USER_ID
        self.session_id = str(uuid.uuid4())[:8] or SESSION_ID
        self.max_iterations = n
        self.state = None

        self.session_service = DatabaseSessionService(DB)
        self.agent = self.agent = Agent(
            model="gemini-2.0-flash-thinking-exp",
            name="OrchestratorAgent",
            instruction=orchestror_prompt,
            #output_schema=Plan,
            tools=single_tools  + [self.planner],
        )
        self.state = None

        self.planner_agent = Agent(
            model="gemini-2.0-flash-thinking-exp",
            name="PlannerAgent",
            instruction=planner_prompt,
            output_schema=Plan,
        )

        self.runner = None

    def planner(self, query: str, prev_results: str = "") -> Plan:
        

        message = f"query: {query} \n previous results: {prev_results} "
        user_content = Content(
            role="user", parts=[Part(text=message)]
        )

        events = self.planner_agent.run_single_turn(
            user_id=self.user_id, session_id=self.session_id, new_message=user_content
        )
        final_response_content = "No response"
        for event in events:
            print(event.content.parts[0].text)

            if event.is_final_response() and event.content and event.content.parts:
                final_response_content = event.content.parts[0].text

        plan = str(Plan.model_validate(final_response_content))
        return plan
    
    async def init_service(self, user_id : str = None,session_id: str = None):
        session_id = session_id or self.session_id
        self.user_id = user_id or self.user_id

        session = await self.session_service.get_session(
            app_name=self.app_name, user_id=self.user_id, session_id=session_id
        )
        if session is None:
            session = await self.session_service.create_session(
                app_name=self.app_name, user_id=self.user_id, session_id=self.session_id
            )
  
        self.runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service
        )

    def run(self, query: str, image : Img = None, filter: Filter = None ,session_id: str = None) -> str:
        parts = [
            Part.from_text(text=query)
        ]
        if image:
            img = b64decode(image.image_base64)
            parts += [Part.from_bytes(data=img, mime_type=f"image/{image.image_type}")]
        

        user_content = Content(
            role="user", parts=parts
        )

        self.session_id = session_id or self.session_id
        final_response_content = "No response"
        events =  self.runner.run(
            user_id=self.user_id, session_id=self.session_id, new_message=user_content
        )
        for event in events:
            print(f"========================= Event ID: {event.id} =========================")
            for part in event.content.parts:
                print(part.text)

            if event.is_final_response() and event.content and event.content.parts:
                final_response_content = event.content.parts[0].text
        return final_response_content

        
# agent_runner.py



from dotenv import load_dotenv
import os


async def main():
    APP_NAME = "videoQA"
    USER_ID = "u_123"
    SESSION_ID = str(uuid.uuid4())[:8]
    load_dotenv()
    DB = os.getenv("DB")
    orc = Orchestrator(DB, USER_ID, SESSION_ID, 5, APP_NAME)
    await orc.init_service()
    orc.run("there is a video of a cat playing with a ball, can you tell me what is the color of the ball?")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

