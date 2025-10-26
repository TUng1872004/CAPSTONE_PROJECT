import inspect
from typing import Callable, Any, Dict, List, Optional, get_type_hints, Annotated
from functools import wraps
from dataclasses import dataclass, field

@dataclass
class FunctionMetadata:
    name: str
    func: Callable
    docstring: str | None
    parameters: dict[str, Any]
    return_type: Any
    category: str
    tags: list[str] = field(default_factory=list)

    def to_dict(self)-> dict:
        return {
            'name': self.name,
            'docstring': self.docstring,
            'parameters': self.parameters,
            'return_type': str(self.return_type),
            'category': self.category,
            'tags': self.tags
        }


class FunctionRegistry:
    """
    Registry for managing and organizing agent tool functions
    Features:
    - Automatic metadata extraction from functions
    - Grouping by category via decorator
    - Query functions by name or category
    - Generate documentation
    """

    def __init__(self):
        self._registry:dict[str,FunctionMetadata] = {}
        self._categories:dict[str, list[str]] = {}
    
    def _extract_metadata(self, func: Callable, category: str, tags: list[str]) -> FunctionMetadata:
        sig = inspect.signature(func)
        parameters = {}
        try:
            type_hints = get_type_hints(func)
        except Exception:
            type_hints = {}
        
        for param_name, param in sig.parameters.items():
            param_info = {
                'type': str(type_hints.get(param_name, param.annotation)),
                'default': param.default if param.default != inspect.Parameter.empty else None,
                'kind': str(param.kind)
            }
            parameters[param_name] = param_info
        
        return_type = type_hints.get('return', sig.return_annotation)
        docstring = inspect.getdoc(func)

        return FunctionMetadata(
            name=func.__name__,
            func=func,
            docstring=docstring,
            parameters=parameters,
            return_type=return_type,
            category=category,
            tags=tags
        )

    def get_function_metadata(
        self,
        name: Annotated[str, "Retrieve the function metadata that is related to the tool usages for the video search retrieval"]
    ) -> FunctionMetadata | None:
        """
        This function will allow user/agent to retrieve the metadata of a tool that is designed specifically for video search/interaction/retrieval/e.tc..
        
        If the function return None, then the tool you search for does not exist.
        """
        return self._registry.get(name)
        

    def register(self, category:str, tags: list[str] | None):
        """
        Decorator to register a func tools
        """
        if tags is None:
            tags = []
        
        def decorator(func: Callable) -> Callable:
            metadata = self._extract_metadata(func, category, tags)
            self._registry[func.__name__] = metadata
            if category not in self._categories:
                self._categories[category] = []
            self._categories[category].append(func.__name__)
            
            @wraps
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
    
        return decorator

    def get_by_category(self, category: Annotated[str, "The category name of a group of function"]) -> List[FunctionMetadata]:
        """Use this function to get all the tools in a specific category, related to video search, moment browse"""
        func_names = self._categories.get(category, [])
        return [self._registry[name] for name in func_names]
    
    def get_by_tag(self, tag: Annotated[str, "List of available tags"]) -> List[FunctionMetadata]:
        """Get all functions with a specific tag."""
        return [
            metadata for metadata in self._registry.values()
            if tag in metadata.tags
        ]
    def list_categories(self) -> List[str]:
        """List all registered categories."""
        return list(self._categories.keys())
    
    def list_functions(self) -> List[str]:
        """List all registered function names."""
        return list(self._registry.keys())





    def generate_documentation(self, category: Annotated[Optional[str], "Optional category for specific function's documentation"] = None) -> str:
        """
        Generate a full function documentation as clear as possible
        """
        doc_lines = ["# Function Registry Documentation\n"]
        
        categories = [category] if category else self.list_categories()
        for cat in sorted(categories):
            functions = self.get_by_category(cat)
            if not functions:
                continue
            doc_lines.append(f"\n## {cat.replace('_', ' ').title()}\n")
            for metadata in functions:
                doc_lines.append(f"\n### `{metadata.name}`\n")
                
                if metadata.docstring:
                    doc_lines.append(f"{metadata.docstring}\n")
                
                if metadata.parameters:
                    doc_lines.append("\n**Parameters:**\n")
                    for param_name, param_info in metadata.parameters.items():
                        param_type = param_info['type']
                        default = param_info['default']
                        default_str = f" = {default}" if default is not None else ""
                        doc_lines.append(f"- `{param_name}` ({param_type}){default_str}\n")
                
                doc_lines.append(f"\n**Returns:** `{metadata.return_type}`\n")
                
                if metadata.tags:
                    doc_lines.append(f"\n**Tags:** {', '.join(metadata.tags)}\n")
        
        return "".join(doc_lines)

    def __repr__(self) -> str:
        return f"FunctionRegistry({len(self._registry)} functions, {len(self._categories)} categories)"

