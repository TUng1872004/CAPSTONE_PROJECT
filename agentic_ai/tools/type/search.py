

from agent.tools.schema.artifact import VideoObject, SegmentObject, ImageObjectInterface




def get_images_from_visual_query(
    query: str,
    list_video_id: list[str],
    top_k: int
) -> list[ImageObjectInterface]:
    """
    From visual query, return the list of images
    Args:
        query: The query that describe the visual images
        list_video_id: list[str]: The video ids that the search will perform upon
    """    


def get_images_from_caption_query(
    query:str,
    list_video_id: list[str],
    top_k:int
) -> list[ImageObjectInterface]:
    """
    
    """


def get_segments_from_visual_query(
    query:str,
    list_video_id: list[str],
    top_k:int
) -> list[ImageObjectInterface]:
    """
    
    """
    


def get_segments_from_caption_query(
    quert:str,
    list_video_id:list[str],
    top_k:int
) -> list[SegmentObject]:
    """
    
    """