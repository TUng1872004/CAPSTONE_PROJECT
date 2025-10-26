"""
This file contains the tools for agents to simulate the human-behaviour to interfact with the video, scanning images...
"""
from agent.tools.schema.artifact import ImageObjectInterface, SegmentObject


##########################
# Segment-based operations
##########################
def get_next_segment(
    current_segment: SegmentObject,
    hop: int,
    include_within_range: bool 
) -> SegmentObject | list[SegmentObject]:
    """
    Given a current segment, return the next segments, based on the hop size
    Args:
        current_segment: 
        hop (int): the hop size
        include_within_range (bool): If True, then all the range within hop is included, else just return the destination segment

    
    """
    return NotImplemented

def get_prev_segment(
    current_segment: SegmentObject,
    hop: int,
    include_within_range: bool 
) -> SegmentObject | list[SegmentObject]:
    """
    Given a current segment, return the previous segments, based on the hop size
    Args:
        current_segment: 
        hop (int): the hop size
        include_within_range (bool): If True, then all the range within hop is included, else just return the destination segment

    
    """
    return NotImplemented






##########################
# Image-based operations
##########################

def get_next_images(
    image: ImageObjectInterface,
    hop: int,
    include_within_range: bool
) -> ImageObjectInterface | list[ImageObjectInterface]:
    """
    
    """

def get_prev_images(
    image: ImageObjectInterface,
    hop: int,
    include_within_range: bool
) -> ImageObjectInterface | list[ImageObjectInterface]:
    """
    
    """

