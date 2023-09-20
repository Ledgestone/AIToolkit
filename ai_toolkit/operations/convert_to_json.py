# convert_to_json.py

import json
from typing import Any
from ai_toolkit.ai_tool import AITool
from ai_toolkit.ai_errors import AINonRetryableError, AIRetryableError

class ConvertToJSON(AITool):
    def __init__(self, name):
        super().__init__(name)
        self.required_input = ["input"]
    
    def _process(self) -> Any:
        input = self._get_from_input("input")
        if not isinstance(input, str):
            raise AINonRetryableError(f"Input must be of type str, not {type(input).__name__}")
        try:
            return json.loads(input)
        except json.decoder.JSONDecodeError as e:
            raise AINonRetryableError(f"Input could not be converted to JSON: {e}")

