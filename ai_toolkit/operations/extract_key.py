# extract_key.py

from typing import Any
from ai_toolkit.ai_tool import AITool
from ai_toolkit.ai_errors import AINonRetryableError, AIRetryableError

class ExtractKey(AITool):
    def __init__(self, name):
        super().__init__(name)
        self.required_input = ["input", "key_name"]
    
    def _process(self) -> Any:
        input = self._get_from_input("input")
        key_name = self._get_from_input("key_name")
        if not isinstance(input, dict):
            raise AINonRetryableError(f"Input must be of type dict, not {type(input).__name__}\nInput: {input}")
        if not isinstance(key_name, str):
            raise AINonRetryableError(f"Key name must be of type str, not {type(key_name).__name__}\nInput: {input}")
        if key_name not in input:
            raise AINonRetryableError(f"Key name '{key_name}' not found in input")
        return input[key_name]

