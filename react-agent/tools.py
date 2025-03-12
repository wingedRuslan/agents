import json
import re
import inspect


class Tool:
    """
    A class representing a Tool for ReAct Agent.
    
    Attributes:
        name (str): Name of the tool.
        description (str): A textual description of what the tool does.
        func (callable): The function this tool wraps.
        arguments (list): A list of argument.
        outputs (str or list): The return type(s) of the wrapped function.
    """
    def __init__(self, 
                 name: str, 
                 description: str, 
                 func: callable, 
                 arguments: list,
                 outputs: str):
        self.name = name
        self.description = description
        self.func = func
        self.arguments = arguments
        self.outputs = outputs

    def to_string(self) -> str:
        """
        Return a string representation of the tool, 
        including its name, description, arguments, and outputs.
        """
        args_str = ", ".join([
            f"{arg_name}: {arg_type}" for arg_name, arg_type in self.arguments
        ])
        
        return (
            f"Tool Name: {self.name}, "
            f"Description: {self.description}, "
            f"Arguments: {args_str}, "
            f"Outputs: {self.outputs}"
        )

    def __call__(self, *args, **kwargs):
        """Invoke the underlying function (callable) with provided arguments."""
        return self.func(*args, **kwargs)


def tool(func):
    """A decorator that creates a Tool instance from the given function."""

    # Get the function signature
    signature = inspect.signature(func)
    
    # Extract (param_name, param_annotation) pairs for inputs
    arguments = []
    for param in signature.parameters.values():
        annotation_name = (
            param.annotation.__name__ 
            if hasattr(param.annotation, "__name__") 
            else str(param.annotation)
        )
        arguments.append((param.name, annotation_name))
    
    # Determine the return annotation
    return_annotation = signature.return_annotation
    if return_annotation is inspect._empty:
        outputs = "No return annotation"
    else:
        outputs = (
            return_annotation.__name__ 
            if hasattr(return_annotation, "__name__") 
            else str(return_annotation)
        )
    
    # Use the function's docstring as the description (default if None)
    description = func.__doc__ or "No description provided."
    
    # The function name becomes the Tool name
    name = func.__name__
    
    # Return a new Tool instance
    return Tool(
        name=name, 
        description=description, 
        func=func, 
        arguments=arguments, 
        outputs=outputs
    )


def parse_action_call_tool(text: str, available_tools: list):
    """
    Extract JSON from a string, parse it, and call the specified Tool from a list.
    
    Args:
        text: String containing JSON inside code blocks
        available_tools: List of Tool objects
        
    Returns:
        Function result or error message
    """
    # Extract the JSON using regex to find content between triple backticks
    json_match = re.search(r'```\s*\n*({.*?})\s*\n*```', text, re.DOTALL)
    
    if not json_match:
        return "No JSON found in the action."
    
    json_str = json_match.group(1)
    
    try:
        # Parse the JSON
        parsed_json = json.loads(json_str)
        
        # Extract function name and arguments
        function_name = parsed_json.get("action")
        arguments = parsed_json.get("action_input", {})
        
        if not function_name:
            return "No action specified in the JSON."
        
        # Find the Tool object with the matching name
        tool = None
        for t in available_tools:
            if t.name == function_name:
                tool = t
                break
        
        if tool is None:
            return f"Tool '{function_name}' not found in available tools."
        
        # Call the function with the provided arguments
        result = tool(**arguments)
        return str(result)
        
    except json.JSONDecodeError:
        return "Invalid JSON format. Repeat again the cycle."

