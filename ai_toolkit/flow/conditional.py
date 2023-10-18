# conditional.py

from typing import Any
from ai_toolkit.flow.process import Process
from ai_toolkit import AITool
from ai_toolkit.ai_errors import AINonRetryableError, AIRetryableError


class Conditional(Process):
    def __init__(self, name):
        super().__init__(name)
        self.required_input = ["condition"]
        self.tool_if_true, self.tool_if_false = None, None

    def _process(self) -> Any:
        condition = self._get_from_input("condition")

        if condition:
            self.output_tool = self.tool_if_true
        else:
            self.output_tool = self.tool_if_false

        return super()._process()

    def expose_output(self, tool_if_true: AITool, tool_if_false: AITool) -> "Conditional":
        if not isinstance(tool_if_true, AITool):
            raise TypeError(
                f"Cannot expose output of {self}, because {tool_if_true} is not an AITool.")
        if not isinstance(tool_if_false, AITool):
            raise TypeError(
                f"Cannot expose output of {self}, because {tool_if_false} is not an AITool.")

        self.tool_if_true = tool_if_true
        self.tool_if_false = tool_if_false
        return self
