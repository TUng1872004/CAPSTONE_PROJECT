from time import time
import os
from PIL import Image
import moondream
from dotenv import load_dotenv
from json_repair import repair_json
import json5

# ---- Optional prompt import ----
try:
    from prompt import MOONDREAM_PROMPT
except ImportError:
    from .prompt import MOONDREAM_PROMPT

# ---- Global model initialization ----
_model = None
_prompt = MOONDREAM_PROMPT


def load_model():
    """
    Lazy-load the Moondream model (only once).
    """
    global _model
    if _model is None:
        load_dotenv()
        api_key = os.getenv("MOONDREAM")
        if not api_key:
            raise ValueError("MOONDREAM API key not found in environment.")
        _model = moondream.vl(api_key=api_key)
    return _model


# ---- Tool definitions ----

def single_caption(path: str, length: str = "short") -> str:
    """
    Generate a caption for a single image.
    Args:
        path (str): Path to the image.
        length (str): Caption length ("short" or "long").
    Returns:
        str: Caption text.
    """
    model = load_model()
    image = Image.open(path)
    response = model.caption(image=image, length=length)
    return response.get("caption", "")


def single_detect(path: str, object_name: str) -> list:
    """
    Detect specified object(s) in an image.
    Args:
        path (str): Path to the image.
        object_name (str): Object to detect.
    Returns:
        list: Detected object data.
    """
    model = load_model()
    image = Image.open(path)
    response = model.detect(image=image, object=object_name)
    return response.get("objects", [])


def single_query(path: str, question: str) -> str:
    """
    Answer a question about a single image.
    Args:
        path (str): Path to the image.
        question (str): Natural language question.
    Returns:
        str: Answer.
    """
    model = load_model()
    image = Image.open(path)
    response = model.query(image=image, question=question, reasoning=True)
    return response.get("answer", "")


# ---- Example local test ----
if __name__ == "__main__":
    setup = time()
    model = load_model()
    print("Model initialized in:", time() - setup)

    test_path = "keyframes/toycar.jpg"
    print("Caption:", single_caption(test_path))
    print("Detect:", single_detect(test_path, "red car"))
    print("Query:", single_query(test_path, "What color is the car?"))
