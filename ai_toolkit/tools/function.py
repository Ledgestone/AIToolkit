# function.py

import json
from typing import List, Dict, Any
from ai_toolkit.ai_tool import AITool
from ai_toolkit.ai_errors import AINonRetryableError, AIRetryableError

class Function(AITool):
    def __init__(self, name):
        super().__init__(name)
        self.required_input = ["function"]
    
    def _process(self) -> Any:
        function_string = self._get_from_input("function")
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
            raise AINonRetryableError(f"Could not convert to a function:\n{function_code}\n\nError: {e}")
    
    def get_input(self, key: str) -> str | Dict[str, Any]:
        return self._get_from_input(key)
