import socket
import json
import uuid

HOST = '127.0.0.1'
PORT = 7000  

def send_query(user_id, session_id, query):
    """Send query via socket and return server response."""
    try:
        with socket.create_connection((HOST, PORT)) as s:
            message = {
                "user_id": user_id,
                "session_id": session_id,
                "query": query
            }
            s.sendall(json.dumps(message).encode())
            s.shutdown(socket.SHUT_WR)
            data = s.recv(4096)
            return data.decode()
    except ConnectionRefusedError:
        return "❌ Cannot connect to the server. Make sure it's running."
    except Exception as e:
        return f"⚠️ Error: {e}"

def terminal_client():
    print("=== ADK Socket Client ===")
    user_id = input("Enter your user_id (default: u_123): ").strip() or "u_123"
    session_id = str(uuid.uuid4())[:8]  # unique session ID per client startup

    query = input("Enter your first query: ").strip()
    if not query:
        print("⚠️ Empty query. Exiting.")
        return

    while True:
        print("\nSending query...")
        response = send_query(user_id, session_id, query)
        print(f"\n🧠 Response: {response}")

        print("\n=== Menu ===")
        print("1. Exit")
        print("2. Ask same question again")
        print("3. Start new session or change question")
        choice = input("Enter your choice (1/2/3): ").strip()

        if choice == "1":
            print("👋 Shutting down client.")
            break

        elif choice == "2":
            print("🔁 Asking the same question again...")
            continue

        elif choice == "3":
            session_id = str(uuid.uuid4())[:8]
            query = input("Enter your new query: ").strip()
            if not query:
                print("⚠️ Empty query. Keeping previous one.")
            else:
                print(f"🆕 Started new session: {session_id}")
        else:
            print("❓ Invalid choice, try again.")


if __name__ == "__main__":
    terminal_client()
