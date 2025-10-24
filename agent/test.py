import socket
import json
import uuid
import base64
from tkinter import Tk, filedialog
from comms import Request, Response

HOST = '127.0.0.1'
PORT = 7000


def send_query(user_id, session_id, query, command = "query",image_obj=None):
    """Send query via socket and return server response."""
    try:
        with socket.create_connection((HOST, PORT)) as s:
            message = {
                "command": command,
                "user_id": user_id,
                "session_id": session_id,
                "query": query
            }

            if image_obj:
                message["image"] =image_obj   # list of base64 strings

            s.sendall(json.dumps(message).encode())
            s.shutdown(socket.SHUT_WR)

            data = s.recv(4096)
            return data.decode()

    except ConnectionRefusedError:
        return "❌ Cannot connect to the server. Make sure it's running."
    except Exception as e:
        return f"⚠️ Error: {e}"


def select_images():
    """Open file dialog for selecting multiple images."""
    root = Tk()
    root.withdraw()  # hide the small tkinter window
    root.wm_attributes('-topmost', 1)  # keep on top
    file_paths = filedialog.askopenfilename(
        title="Select Image Files",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp")]
    ) # Add a 's' to get multiple file
    root.destroy()
    # return list(file_paths)
    return file_paths

def encode_images_to_base64(path):
    """Convert image paths into list of base64 strings."""
    try:
        with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"⚠️ Failed to read {path}: {e}")
    return encoded


def run():
    print("=== ADK Socket Client ===")
    user_id = "u_123"
    session_id = str(uuid.uuid4())[:8]

    while True:
        print("\nSending query...")
        command = "query"
        img_obj = None
        print("\n=== Menu ===")
        print("1. query")
        print("2. Ask same question again")
        print("3. Start new session or change question")
        print("4. Upload with pics 📸")
        print("5. Shutdown")
        choice = input("*******  Enter your choice (1/2/3/4/5): ").strip()
        session_id = None
        if choice == "5":
            print("👋 Shutting down client.")
            command = "shutdown"
            break
        elif choice == "1":
            query = input(f"Enter your {"new " if not session_id else ""}query: ").strip()

        elif choice == "2":
            print("🔁 Asking the same question again...")
            command = "query"
            continue

        elif choice == "3":
            session_id = str(uuid.uuid4())[:8]
            query = input("Enter your new query: ").strip()
            if not query:
                print("⚠️ Empty query. Keeping previous one.")
            else:
                print(f"🆕 Started new session: {session_id}")

        elif choice == "4":
            print("🪟 Opening file dialog...")
            image_paths = select_images()

            if not image_paths:
                print("⚠️ No images selected.")
                continue
            

            encoded_images = encode_images_to_base64(image_paths)
            print(f"{type(image_paths)} : {image_paths}")
            img_obj=    {
                    "image_base64":encoded_images,
                    "image_type": image_paths.split(".")[-1]
                                    }

            query = input("Enter your query for these images: ").strip()
            if not query:
                print("⚠️ Empty query, skipping.")
                continue

            print("📨 Sending query with images...")
            

        else:
            print("❓ Invalid choice, try again.")

        session_id = session_id or str(uuid.uuid4())[:8]
        response = send_query(user_id, session_id, query,command, img_obj)
        print(f"\n💬 Response: {response}")


if __name__ == "__main__":
    run()
