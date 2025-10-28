"""
This will contain a bunch of agent as tools
"""
from typing import Annotated


async def enhance_visual_query(
    raw_query: Annotated[str, "Raw user query"],
    variants: Annotated[list[str], "Kind of variants description, visually"]
) -> list[str]:
    """
    
    """


async def enhance_textual_query(
    raw_query: Annotated[str, "Raw user query"],
    variants: Annotated[list[str], "Kind of variants description, in terms of events"]
) -> list[str]:
    """
    
    """
    
