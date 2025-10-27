
from llama_index.core.llms import ChatMessage
from pydantic import BaseModel, Field

from .agents import WorkersPlan 



class PlannerState(BaseModel):
    plan: WorkersPlan | None = Field(...)
    plan_description: str 


class GreetingState(BaseModel):
    """
    This is the State of the greeting agent, where it will leave its thought here
    """
    choose_next_agent: str | None = Field(None, description="Choosing the next agent to run, or None, meaning passing the result to the user")
    reason: str = Field('', description="Why did you make this decision")
    passing_message: str | None = Field(..., description="The message that the agent want another agent to know")

    

class AgentState(BaseModel):
    chat_history: list[ChatMessage] = Field(default_factory=list, description="The persistent chat history")
    greeting_state: GreetingState = Field(default_factory=lambda: GreetingState()) #type:ignore

    planner_state: PlannerState = Field(default_factory=lambda: PlannerState())#type:ignore

    

