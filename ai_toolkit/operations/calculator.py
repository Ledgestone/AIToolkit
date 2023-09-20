# calculator.py

from typing import Any
from ai_toolkit.ai_tool import AITool
from ai_toolkit.ai_errors import AINonRetryableError, AIRetryableError

class Calculator(AITool):
    def __init__(self, name):
        super().__init__(name)
        self.required_input = ["expression"]
    
    def _process(self) -> Any:
        expression = self._get_from_input("expression")
        try:
            return eval(expression)
        except Exception as e:
            raise AINonRetryableError(f"Could not evaluate the following code:\n{expression}\n\nError: {e}")
