from .md import single_caption, single_detect, single_query
from llama_index.core.tools import FunctionTool, ToolMetadata


single_tools = [
    FunctionTool(
        fn=single_caption,
        metadata=ToolMetadata(
            name="single_caption",
            description="Get the caption of a single frame given its path or index"
        )
    ),
    FunctionTool(
        fn=single_detect,
        metadata=ToolMetadata(
            name="single_detect",
            description="Detect a specific object in a single frame given its path or index and object name"
        )
    ),
    FunctionTool(
        fn=single_query,
        metadata=ToolMetadata(
            name="single_query",
            description="Answer a question about a single frame given its path or index and a question string"
        )
    )
]

complex_tools = [
    
]
__all__ = single_tools + complex_tools



import random

def generate_random_number(low: float = 0, high: float = 1) -> float:
    """Generate a random number between 'low' and 'high'."""
    return random.uniform(low, high)

random_tool = [FunctionTool(
    fn=generate_random_number,
    metadata=ToolMetadata(
        name="generate_random_number",
        description="Generate a random number between 'low' and 'high' (inclusive)."
    ),
)]
