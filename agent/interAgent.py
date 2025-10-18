import asyncio
from comms import Request, Response
import json
from orchestrator import Orchestrator


async def handle_client(reader, writer):
    try:
        data = await reader.read(4096)
        message = data.decode().strip()
        print(f"Received: {message}")
        payload = json.loads(message)

        user_id = payload.get("user_id", "u_1")
        session_id = payload.get("session_id", "s_1")
        query = payload.get("query")
        filter = payload.get("filter", {})
        if not query:
            response = {"error": "Missing 'query'"}
        else:
            orc = Orchestrator(user_id, session_id)
            await orc.init_service()
            result = await orc.run(query)
            response = {"response": result}

        response_str = json.dumps(response) + "\n"
        writer.write(response_str.encode())
        await writer.drain()

    except Exception as e:
        writer.write(json.dumps({"error": str(e)}).encode())
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 7000)
    addr = server.sockets[0].getsockname()
    print(f"Socket server started on {addr}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())