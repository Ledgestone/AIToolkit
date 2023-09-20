# passthrough.py

from typing import Any
from ai_toolkit.ai_tool import AITool

class Passthrough(AITool):
    def __init__(self, name):
        super().__init__(name)
        self.required_input = ["name_of_input"]
    
    def _process(self) -> Any:
        return self._get_from_input(self._get_from_input("name_of_input"))

