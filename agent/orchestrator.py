from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from google.adk.agents import Agent


if __name__ == "__main__":
    from prompt import *  
    from schema import *
    from tools import single_tools

class Orchestrator:
    def __init__(self,USER_ID, SESSION_ID, n: int = 3, APP_NAME: str = "videoQA"):
        self.app_name = APP_NAME
        self.user_id = USER_ID
        self.session_id = f"{self.user_id}_{SESSION_ID}"
        self.max_iterations = n
        self.state = None

        self.session_service = InMemorySessionService()
        self.agent = self.agent = Agent(
            model="gemini-2.0-flash-thinking-exp",
            name="OrchestratorAgent",
            instruction=orchestror_prompt,
            output_schema=Plan,
            #tools=single_tools,

        )
        self.state = None

    async def init_service(self):
        
        session = await self.session_service.get_session(
            app_name=self.app_name, user_id=self.user_id, session_id=self.session_id
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

    def run(self, query: str):
        message = f"query: {query} "
        user_content = Content(
            role="user", parts=[Part(text=message)]
        )

        final_response_content = "No response"
        events =  self.runner.run(
            user_id=self.user_id, session_id=self.session_id, new_message=user_content
        )
        for event in events:
            print(event.content.parts[0].text)

            if event.is_final_response() and event.content and event.content.parts:
                final_response_content = event.content.parts[0].text
        return final_response_content

        
# agent_runner.py



from dotenv import load_dotenv
import os


async def main():
    APP_NAME = "videoQA"
    USER_ID = "u_123"
    SESSION_ID = "s_123"
    load_dotenv()
    orc = Orchestrator(USER_ID, SESSION_ID, 1, APP_NAME)
    await orc.init_service()
    orc.run("there is a video of a cat playing with a ball, can you tell me what is the color of the ball?")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

