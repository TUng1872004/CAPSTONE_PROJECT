import asyncio
from comms import Request, Response, Img
import json
from orchestrator import Orchestrator
import uuid


shutdown_event = asyncio.Event()

async def handle_client(orc, reader, writer):
    try:
        buffer = b""
        while True:
            chunk = await reader.read(4096)
            if not chunk:
                break
            buffer += chunk
            try:
                payload = json.loads(buffer.decode().rstrip('\r\n'))
                break
            except json.JSONDecodeError as e:
                continue

        
        #payload = json.loads(message)
        command = payload.get("command")
        if command == "shutdown":
            response = {"status": "Server shutting down..."}
            writer.write((json.dumps(response) + "\n").encode())
            await writer.drain()
            shutdown_event.set()   # Trigger global shutdown
            return
        
        user_id = payload.get("user_id", None)
        session_id = payload.get("session_id", None)
        query = payload.get("query")
        filter = payload.get("filter", {})
        if user_id is not None and orc.user_id != user_id:
            await orc.init_service(user_id, session_id)
        if not query and command != "query":
            response = {"error": "Missing 'query'"}
        else:
            img_obj =payload.get("image", None)
            if img_obj:
                img_obj = Img.model_validate(img_obj)
            result = orc.run(query, img_obj)
            response = {"response": result}

        response_str = json.dumps(response) + "\n"
        writer.write(response_str.encode())
        await writer.drain()

    except Exception as e:
        writer.write(json.dumps({"error": str(e)}).encode())
    finally:
        writer.close()
        await writer.wait_closed()


from dotenv import load_dotenv
from os import getenv
import functools
async def main():
    from time import time
    start = time()
    load_dotenv()
    DB = getenv("DB")
    orc = Orchestrator(DB)
    server = await \
                    asyncio.start_server(functools.partial(handle_client, orc), 
                                        "127.0.0.1", 
                                        7000)
    addr = server.sockets[0].getsockname()
    print(f"Socket server started on {addr} takes {time()-start:.2f}s")

    async with server:
        await shutdown_event.wait()
        print("🛑 Shutdown signal received, closing server...")
        server.close()
        await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())