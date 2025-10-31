import uuid, base64, requests
from typing import Optional

URL = "http://127.0.0.1:8000/query"

def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def build_image_obj(path: str) -> dict:
    return {
        "image_base64": encode_image(path),
        "image_type": path.split(".")[-1]
    }

def send_query(
    user_id: str,
    session_id: str,
    query: str,
    image_path: Optional[str] = None,
    filter_obj: Optional[dict] = None
) -> dict:
    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "query": query,
        "image": build_image_obj(image_path) if image_path else None,
        "filter": filter_obj
    }
    res = requests.post(URL, json=payload)
    try:
        return res.json()
    except Exception:
        return {"error": res.text}

def cli():
    user_id = "u_123"
    session_id = str(uuid.uuid4())[:8]
    while True:
        print("\n1.query  2.new session  3.image  4.exit")
        c = input("> ").strip()
        if c == "4":
            break
        if c == "1":
            q = input("query: ").strip()
            print(send_query(user_id, session_id, q))
        elif c == "2":
            session_id = str(uuid.uuid4())[:8]
            q = input("new query: ").strip()
            print(send_query(user_id, session_id, q))
        elif c == "3":
            p = input("image path: ").strip()
            q = input("query: ").strip()
            print(send_query(user_id, session_id, q, p))

if __name__ == "__main__":
    cli()
