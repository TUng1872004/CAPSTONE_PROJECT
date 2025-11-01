"""
The main agent that we will call uponn
"""

from typing import List, Any, Annotated, cast
import asyncio

from llama_index.core.workflow import Workflow, step, Context
from llama_index.core.llms import LLM, ChatMessage
from llama_index.core.tools import BaseTool
from llama_index.core.agent.workflow import AgentStream
from llama_index.core.agent.workflow import ToolCall
from llama_index.core.workflow.handler import WorkflowHandler # type:ignore


if __name__=="__main__":
    from state import AgentState

    from events import (
        UserInputEvent,
        FinalResponseEvent,
        AgentProgressEvent,
        AgentResponse,
        PlannerInputEvent,
        PlanProposedEvent,
        ExecutePlanEvent,
        AllWorkersCompleteEvent
    )

    from agents import (
        create_greeting_agent,
        create_planner_agent,
        create_orchestrator_agent,
        create_worker_agent,
        create_consolidation_agent
    )

    from schema import (
        WorkerBluePrint,
        WorkersPlan
    )
else:
    from .state import AgentState

    from .events import (
        UserInputEvent,
        FinalResponseEvent,
        AgentProgressEvent,
        AgentResponse,
        PlannerInputEvent,
        PlanProposedEvent,
        ExecutePlanEvent,
        AllWorkersCompleteEvent
    )

    from .agents import (
        create_greeting_agent,
        create_planner_agent,
        create_orchestrator_agent,
        create_worker_agent,
        create_consolidation_agent
    )

    from .schema import (
        WorkerBluePrint,
        WorkersPlan
    )


async def _stream_event(handler: WorkflowHandler, ctx: Context[AgentState], agent_name: str) -> str:
    print("Hello")
    message_stream_list = []
    async for event in handler.stream_events():
        if isinstance(event, AgentStream):
            message_stream = event.delta
            message_stream_list.append(message_stream)

            ctx.write_event_to_stream(
                AgentResponse(
                    agent_name=agent_name,
                    message=''.join(message_stream_list)
                )
            )
        
    return ''.join(message_stream_list)

class VideoAgentWorkFlow(Workflow):
    """
    Multi-agent orchestration with HIL plan approval
    
    Flow:
        User -> greeting agent -> Planner -> [Plan Review Loop] -> Orchestrator -> Workers -> Response

    The workflow STOPS at plan proposal, waits for user feedback, then continues.
    """

    def __init__(
        self,
        llm: LLM, 
        context_tools: Annotated[list[BaseTool], "A list of functions that expose the tools of the system, so the agent can reason upon"],
        all_tools: Annotated[dict[str, BaseTool], "All the tools related to video search stuff"],
        logger,
        timeout: float = 600.0,
        verbose: bool = True
    ):
        super().__init__(timeout=timeout, verbose=verbose)
        
        self.llm = llm
        self.context_tools = context_tools
        self.all_tools = all_tools
        
        self.greeting_agent = create_greeting_agent(llm=llm)
        self.orchestrator_agent = create_orchestrator_agent(llm=llm, all_tools=all_tools)
        self.consolidator = create_consolidation_agent(llm)
        
        self.logger = logger
        self.ctx = AgentState()

 


    @step
    async def handle_greeting(
        self,
        ctx: Context[AgentState],
        ev: UserInputEvent
    ) -> FinalResponseEvent | PlannerInputEvent:

        self.ctx = ctx
        #print("====== start setting state ======")
        #await ctx.store.set('state', AgentState())
        #print("====== finish setting state ======\n\n")
        chat_history = ev.chat_history.copy()
        chat_history.append(
            ChatMessage(role='user', content=ev.input)
        )
        user_message = ev.input
        
        print("====== setup chat history ======")
        async with ctx.store.edit_state() as state:
            state.chat_history = chat_history
        print("====== finish setup chat history ======\n\n")
        await ctx.write_event_to_stream(
            AgentProgressEvent(
                agent_name=self.greeting_agent.name,
                message="I am reading your request..."
            )
        )

        handler = await self.greeting_agent.run(
            user_msg=ev.input,
            chat_history=chat_history
        )
        print("GreetingAgent.run() returned:", handler)
        full_response = await _stream_event(handler=handler, ctx=ctx, agent_name=self.greeting_agent.name)

        print("\n\n===== Greeting response ===== \n",full_response)
        next_agent = await ctx.store.get('greeting_state.choose_next_agent')
        reason = await ctx.store.get('greeting_state.reason')
        passing_message = await ctx.store.get('greeting_state.passing_message')

        self.ctx = ctx
        if next_agent == "planner": 
            chat_history.append(
                ChatMessage(role="assistant", content=str(full_response))
            )

            return PlannerInputEvent(
                user_msg=user_message,
                planner_demand="\n\n".join([reason + passing_message])
            )

        else:
            return FinalResponseEvent(
                response=str(full_response)
            )
    
    @step
    async def planning(
        self,
        ctx: Context[AgentState],
        ev: PlannerInputEvent
    ) -> PlanProposedEvent:
        
        planning_agent = create_planner_agent(llm=self.llm, registry_tools=self.context_tools)

        ctx.write_event_to_stream(
            AgentProgressEvent(
                agent_name=planning_agent.name,
                message="Analyzing user request and creating plan for video deep researching..."
            )
        )

        user = ev.user_msg
        message = f"The original user message: {ev.user_msg}. And here is the instruction of the greeting agent. {ev.planner_demand}"


        handler = planning_agent.run(user_msg=message)

        full_response = await _stream_event(handler=handler, ctx=ctx, agent_name=planning_agent.name)

        
        plan_description = await ctx.store.get('planner_state.plan_description')
        plan_detail = await ctx.store.get('planner_state.plan')
        print(f"Plan detail: {plan_detail}")

        self.ctx = ctx
        return PlanProposedEvent(
            user_msg=user,
            agent_response=full_response,
            plan_detail=plan_detail,
            plan_summary=plan_description
        )
    

    
    @step
    async def verify_plan(
        self,
        ctx: Context[AgentState],
        ev: PlanProposedEvent
    ) -> ExecutePlanEvent | PlannerInputEvent:
        """
        Orchestrator reviews the proposed plan from the planner.
        If the plan is good, it proceeds to execution.
        Otherwise, it requests a revised plan.
        """
        self.ctx = ctx
        ctx.write_event_to_stream(
            AgentResponse(
                agent_name="Orchestrator Agent",
                message="Checking on plan"
            )
        )
        orc = self.orchestrator_agent
        handler = orc.run(user_msg=f"Verify if the plan is acceptable: {ev}")

        try:
            full_response = await _stream_event(handler=handler, ctx=ctx, agent_name=orc.name)
            print("Agent response received successfully")
        except Exception as e:
            print.exception("Error while streaming event from orchestrator")
            raise

        if "approved" in full_response.lower() in full_response.lower():
            print("Plan approved")
            return ExecutePlanEvent(plan=ev)
        else:
            print("Plan rejected, re-requesting input")
            return PlannerInputEvent(reason="Plan needs revision")
        
    @step
    async def execute_approved_plan(
        self,
        ctx: Context[AgentState],
        ev: ExecutePlanEvent
    ) -> AllWorkersCompleteEvent: # fix bug
        ctx.write_event_to_stream(
            AgentResponse(
                agent_name="Orchestrator Agent",
                message="Spawning worker agents"
            )
        )

        plan = ev.plan


        def create_code_executor_for_worker(worker_tools: list[BaseTool]):
            """
            Creates a restricted async code executor for worker agents.
            Exposes only allowed tools in a controlled environment.
            """

            async def executor(code: str) -> Any:
                allowed_tools = {tool.name: tool.fn for tool in worker_tools}

                safe_globals = {"__builtins__": {"print": print, "range": range, "len": len}}
                safe_locals = allowed_tools.copy()

                async def _run_async_code():
                    try:
                        exec(
                            f"async def __worker_fn__():\n"
                            + "\n".join(f"    {line}" for line in code.splitlines()),
                            safe_globals,
                            safe_locals,
                        )
                        return await safe_locals["__worker_fn__"]()
                    except Exception as e:
                        return f"Execution error: {type(e).__name__}: {e}"

                try:
                    return await _run_async_code()
                except Exception as e:
                    return f"Worker runtime error: {type(e).__name__}: {e}"

            return executor

        
        async def run_worker(idx: int, blueprint: WorkerBluePrint, ctx: Context | None = None):
            worker_name = blueprint.name
            ctx.write_event_to_stream(
                AgentProgressEvent(
                    agent_name=worker_name,
                    message=f"Starting task: {blueprint.task}"
                )
            )

            worker_tool_names = blueprint.tools
            worker_tools = [
                self.all_tools[tool_name] for tool_name in worker_tool_names if tool_name in self.all_tools
            ]

            """
            Spawning worker agent env
            """
            code_execute_fn = create_code_executor_for_worker(worker_tools)

            worker = create_worker_agent(
                llm=self.llm,
                name=worker_name,
                description=blueprint.get("description", ""),
                tools=worker_tools,
                code_execute_fn=code_execute_fn
            )

            try:
                result = await worker.run(
                    user_msg=blueprint.task,
                    ctx=ctx 
                )
                ctx.write_event_to_stream(
                    AgentProgressEvent(
                        agent_name=worker_name,
                        message=f"✅ Completed: {blueprint.task}"
                    )
                )
                return {
                    'worker_name': worker_name,
                    'task': blueprint.task,
                    'result': str(result),
                    'success': True
                }

            except Exception as e:
                ...
            
        
        worker_tasks = [
            asyncio.create_task(run_worker(idx, cast(WorkerBluePrint,blueprint))) for idx, blueprint in enumerate(plan)
        ]
        result = await asyncio.gather(*worker_tasks)
        ### prepare the content for the final orchestration
        self.ctx = ctx
        return AllWorkersCompleteEvent(
            user_msg = ev.user_msg,
            result=result
        )
    

    @step
    async def consolidate_results(
        self, 
        ctx: Context,
        ev: AllWorkersCompleteEvent
    ) -> FinalResponseEvent:
        
        ctx.write_event_to_stream(
            AgentProgressEvent(
                agent_name=self.consolidator.name,
                message="Consolidating results..."
            )
        )
        con = self.consolidator.name
        handler = con.run(user_msg=f"{ev}")

        full_response = await _stream_event(handler=handler, ctx=ctx, agent_name=con.name)
        self.ctx = ctx
        return FinalResponseEvent(response=full_response)



    