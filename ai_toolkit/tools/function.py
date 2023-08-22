# function.py

import json
from typing import List, Dict, Any
from ai_toolkit.ai_tool import AITool
from ai_toolkit.ai_errors import AINonRetryableError, AIRetryableError

class Function(AITool):
    PREDEFINED_FUNCTIONS = [
        "passthrough", 
        "convert_to_json",
        "extract_key"
    ]
    def __init__(self, name):
        super().__init__(name)
        self.required_input = ["function"]
        self.optional_input = ["name_of_input", "input", "key_name"]
    
    def _process(self) -> Any:
        function_string = self._get_from_input("function")

        # If the function is a predefined function, call it
        # otherwise, attempt to convert the string input to a function
        # and call it
        if function_string in Function.PREDEFINED_FUNCTIONS:
            return getattr(self, function_string)()
            
        try:
            local_vars = {
                "get_input": self.get_input,
                "result": None
            }
            function_code = f"""
def user_func(get_input):
    {function_string}

result = user_func(get_input)
"""
            exec(function_code, {}, local_vars)
            return local_vars["result"]
        except Exception as e:
            raise AINonRetryableError(f"Could not convert to a function:\n{function}\n\nError: {e}")
    
    def get_input(self, key: str) -> str | Dict[str, Any]:
        return self._get_from_input(key)
    
    def passthrough(self) -> Any:
        if "name_of_input" in self.input:
            return self.get_input(self.get_input("name_of_input"))
        return self.get_input("input")
    
    def convert_to_json(self) -> Any:
        if "name_of_input" in self.input:
            input = self.get_input(self.get_input("name_of_input"))
        else:
            input = self.get_input("input")
        if not isinstance(input, str):
            raise AINonRetryableError(f"Input must be of type str, not {type(input).__name__}")
        try:
            return json.loads(input)
        except json.decoder.JSONDecodeError as e:
            raise AINonRetryableError(f"Input could not be converted to JSON: {e}")
        
    def extract_key(self) -> Any:
        if "name_of_input" in self.input:
            input = self.get_input(self.get_input("name_of_input"))
        else:
            input = self.get_input("input")
        key_name = self.get_input("key_name")
        if not isinstance(input, dict):
            raise AINonRetryableError(f"Input must be of type dict, not {type(input).__name__}\nInput: {input}")
        if not isinstance(key_name, str):
            raise AINonRetryableError(f"Key name must be of type str, not {type(key_name).__name__}\nInput: {input}")
        if key_name not in input:
            raise AINonRetryableError(f"Key name '{key_name}' not found in input")
        return input[key_name]
