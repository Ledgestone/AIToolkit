# passthrough.py

from typing import Any
from ai_toolkit.ai_tool import AITool

class Passthrough(AITool):
    """
    A passthrough tool simply takes an input and returns it as an output. It is useful
    for changing the name of an input key.

    Required input:
        name_of_input: Any --- The name of the input to pass through

    Dynamic input:
        Must be the value oe the name_of_input input

    Output:
        The value of the input

    Example:
    ```python
    passthrough = ai.operations.Passthrough("Passthough").set_input(
            name_of_input="custom_input", 
            custom_input="value")
    ```
    """
    def __init__(self, name):
        super().__init__(name)
        self.required_input = ["name_of_input"]
    
    def _process(self) -> Any:
        return self._get_from_input(self._get_from_input("name_of_input"))

