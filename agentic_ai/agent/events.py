from typing import Any
from pydantic import Field
from llama_index.core.workflow import StartEvent, StopEvent, Event
from llama_index.core.llms import ChatMessage

from .schema import WorkersPlan


class UserInputEvent(StartEvent):
    user_msg: str


class FinalResponseEvent(StopEvent):
    response: str 

class PlannerInputEvent(Event):
    user_msg: str
    planner_demand: str
    


class PlanProposedEvent(Event):
    agent_response: str
    plan_summary: str
    plan_detail: WorkersPlan



# Progress and streaming events
class AgentProgressEvent(Event):
    agent_name: str
    message: str


class AgentResponse(Event):
    agent_name: str
    message: str




class ExecutePlanEvent(Event):
    plan: WorkersPlan
    plan_description: str
    user_msg: str
    agent_demand: str


class AllWorkersCompleteEvent(Event):
    result: list
    