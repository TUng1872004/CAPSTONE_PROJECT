import asyncio
import logging
import sys
from pathlib import Path
import uuid
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich import box
from llama_index.core.llms import ChatMessage, MessageRole
 
from client import WorkflowClient
from session import SessionManager
from event_handler import EventHandler

from llama_index.core.evaluation import AnswerRelevancyEvaluator, EvaluationResult, CorrectnessEvaluator
from llama_index.llms.gemini import Gemini

from datetime import datetime
import json
async def evaluate_response(query: str, response: str, contexts: list[str], reference :str = None) -> EvaluationResult:
    evaluator_llm = Gemini(temperature = 0.0)

    res = {}
    relevancy_evaluator = AnswerRelevancyEvaluator(llm=evaluator_llm)
    relevant: EvaluationResult = await relevancy_evaluator.aevaluate(
                                        query=query, 
                                        response=response,    
                                        contexts=contexts
                                    )
    res["relevancy"] = relevant
    if reference:
 
        exact_match_evaluator = CorrectnessEvaluator()
        exact_match: EvaluationResult = await exact_match_evaluator.aevaluate(
                                            query=query,
                                            response=response,
                                            reference=reference
                                        )
        res["correctness"] = exact_match
    return res

    
async def run_test(client: WorkflowClient, console: Console, session_manager: SessionManager, user_id: str, list_video_ids: list[str], session_id: str, q_list: list[str]):
    
    with open("test.json", 'r') as f:
        res = json.load(f)
    for user_input in q_list:
        session = session_manager.load_session(user_id, session_id)
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_chat_message = await client.execute_workflow(
            user_demand=user_input,
            video_ids=list_video_ids,
            chat_history=session.chat_history,
            session_id=session_id
        )
        
        if final_chat_message:
            final_message = final_chat_message
            session.add_message(final_message)
            session_manager.save_session(session)
            try:
                    context = [m.content for m in final_chat_message][:-5]
                    response = final_chat_message[-1].content

                    eval = await evaluate_response(query=user_input, response=response, contexts=context)

                    res.append({
                        "query": user_input,
                        "response": response,
                        "evaluation": eval
                    })
                            
                    
            except Exception as e:
                    try:
                        er = json.dumps({"error": str(e) + f"\n{type(response)}"})  
                    except:
                        er = {"error": "Unknown error during evaluation"}
                    res.append(er)
            with open("test.json", "w", encoding="utf-8") as f:
                    json.dump(res, f, ensure_ascii=False, indent=4)
            
            
        else:
            console.print("\n[yellow]⚠[/yellow] Workflow completed without final response", style="dim")

async def run_interactive_session(test_session_dir: Path, user_id: str, list_video_ids:list[str], q_list: list[str] = None):
    for name in ("websockets", "websockets.client", "websockets.server", "websockets.protocol"):
        logging.getLogger(name).setLevel(logging.WARNING)

    console = Console()
    session_dir = test_session_dir / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)

    session_manager = SessionManager(session_dir)
    event_handler = EventHandler(console=console)
    websocket_url = "ws://localhost:8050/ws/start_workflow"
    if q_list is None:
        console.print(Panel.fit(
            "[bold cyan]🎬 Video Deep Search Workflow Client[/bold cyan]\n"
            "[dim]Interactive CLI for testing workflow services[/dim]",
            border_style="cyan",
            box=box.DOUBLE
        ))

        console.print()
        session_id = Prompt.ask("[bold magenta]Enter session_id (Press Enter to create a new one): [/bold magenta]").strip()
    
   
        if not session_id:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            console.print(f"[green]✓[/green] Created new session with ID: [cyan]{session_id}[/cyan]")
    else:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    console.print("\n[bold yellow]Available Commands:[/bold yellow]")
    console.print("  [cyan]•[/cyan] Type your question to start workflow")
    console.print("  [cyan]•[/cyan] [bold]history[/bold] - View chat history")
    console.print("  [cyan]•[/cyan] [bold]clear[/bold] - Clear session")
    console.print("  [cyan]•[/cyan] [bold]exit[/bold] or [bold]quit[/bold] - Quit\n")
    
    client = WorkflowClient(
        websocket_url=websocket_url,
        user_id=user_id,
        event_handler=event_handler
    )
    if q_list is not None:
        await run_test(client, console, session_manager, user_id, list_video_ids, session_id, q_list)
    while True:
        session = session_manager.load_session(user_id, session_id)

        with open("test.json", 'r') as f:
            res = json.load(f)
        try:
            console.print()
            console.print(Panel(
                f"[green]✓[/green] Session loaded: [bold]{len(session.chat_history)}[/bold] messages in history\n"
                f"[dim]User:[/dim] [cyan]{user_id}[/cyan]\n"
                f"[dim]Last updated:[/dim] {session.updated_at}",
                title="[bold]Session Info[/bold]",
                border_style="green",
                box=box.ROUNDED
            ))

            user_input = Prompt.ask("[bold magenta]You[/bold magenta]").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit']:
                console.print("\n[bold green]👋 Goodbye![/bold green]")
                break
            
            if user_input.lower() == 'history':
                session.display_history(console)
                continue
            
            if user_input.lower() == 'clear':
                session.clear_history()
                session_manager.save_session(session)
                console.print("[green]✓[/green] Session cleared", style="bold")
                continue
            
            
            console.print()
            console.rule("[bold cyan]Starting Workflow[/bold cyan]", style="cyan")
            console.print()
            
            final_chat_message = await client.execute_workflow(
                user_demand=user_input,
                video_ids=list_video_ids,
                chat_history=session.chat_history,
                session_id=session_id
            )
            
            if final_chat_message:
                final_message = final_chat_message
                session.add_message(final_message)
                session_manager.save_session(session)
                
                console.print()
                console.print(Panel(
                    "[green]✓[/green] Workflow complete. Session saved.",
                    border_style="green",
                    box=box.ROUNDED
                ))
                try:
                    context = [m.content for m in final_chat_message][:-5]
                    response = final_chat_message[-1].content

                    eval = await evaluate_response(query=user_input, response=response, contexts=context)

                    res.append({
                        "query": user_input,
                        "response": response,
                        "evaluation": eval
                    })
                            
                    
                except Exception as e:
                    try:
                        er = json.dumps({"error": str(e) + f"\n{type(response)}"})  
                    except:
                        er = {"error": "Unknown error during evaluation"}
                    res.append(er)
                with open("test.json", "w", encoding="utf-8") as f:
                            json.dump(res, f, ensure_ascii=False, indent=4)

            else:
                console.print("\n[yellow]⚠[/yellow] Workflow completed without final response", style="dim")

        except KeyboardInterrupt:
            console.print("\n\n[yellow]⚠ Interrupted by user[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red]✗ Error:[/bold red] {e}")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")


if __name__ == "__main__":
    test_session_dir = Path('../local')
    user_id = 'testagent'
    list_video_ids = []
    mode = 2
    if mode == 2:
        with open("question.json", 'r') as f:
            question_list = json.load(f)
    else:
         question_list  = None
    try:
        asyncio.run(run_interactive_session(test_session_dir=test_session_dir, user_id=user_id, list_video_ids=list_video_ids,q_list=question_list))
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[bold green]👋 Goodbye![/bold green]")
        sys.exit(0)
    
