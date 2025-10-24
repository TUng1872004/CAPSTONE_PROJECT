from .md import single_caption, single_detect, single_query
from image_analysis import IwI

single_tools = [
    single_caption,
    single_detect,
    single_query
]
complex_tools = [
    IwI
]
__all__ = single_tools + complex_tools