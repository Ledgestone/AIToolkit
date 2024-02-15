# process.py

from ai_toolkit.ai_tool import AITool
from typing import List, Dict, Any, Set
from ai_toolkit.ai_errors import AINonRetryableError, AIRetryableError


class Process(AITool):
    def __init__(self, name):
        super().__init__(name)
        self.output_tool: AITool = None
        self.process_inputs: Dict[str, "_ProcessInput"] = dict()

    def _process(self) -> Any:
        self._process_all_inputs()
        self._process_all_tools()

        return self.output_tool.get_output()

    def _process_all_inputs(self) -> None:
        ai_tools = self.ai_tools_in_process()
        for ai_tool in ai_tools:
            if not ai_tool._has_inputs_connected():
                raise AINonRetryableError(
                    f"Cannot process {self}, because {ai_tool} does not have all its required inputs connected.")

        for process_input in self.process_inputs.values():
            process_input.process()

    def _process_all_tools(self) -> None:
        ai_tools = self.ai_tools_in_process()
        still_processing = True
        processed_tools = list()
        while still_processing:
            still_processing = False
            # Loop through the not processed tools
            for ai_tool in [ai_tool for ai_tool in ai_tools if ai_tool not in processed_tools]:
                if ai_tool.can_process():
                    print(f"Processing {ai_tool}")
                    ai_tool.process()
                    processed_tools.append(ai_tool)
                    still_processing = True

        # Make sure all the tools have processed
        if len(processed_tools) != len(ai_tools):
            unprocessed_tools = [
                ai_tool for ai_tool in ai_tools if ai_tool not in processed_tools]
            raise AIRetryableError(
                f"Cannot finish processing {self}, because the following tools could not be processed: {unprocessed_tools}")

    def set_input(self, **kwargs) -> "Process":
        for key, value in kwargs.items():
            if key in self.process_inputs:
                self.process_inputs[key].set_input(**{key: value})
            else:
                self.process_inputs[key] = _ProcessInput(
                    self).set_input(**{key: value})
                self.dynamic_input.append(key)

            # If the value is an AITool, add it to the dependencies, and add to the dependents of the AITool
            if isinstance(value, AITool):
                self.dependencies.append(value)
                value._add_dependent(self)

            self.input[key] = value

        return self

    def expose_input(self, key: str, tool: AITool) -> "Process":
        if key in self.process_inputs:
            tool.set_input(**{key: self.process_inputs[key]})
        else:
            self.process_inputs[key] = _ProcessInput(self)
            tool.set_input(**{key: self.process_inputs[key]})
            self.dynamic_input.append(key)

        return self

    def reset_process(self) -> None:
        # Set the output to None for all the process inputs and all the tools in the process.
        # If an ai tool in the process is a process, then reset that process as well.
        for process_input in self.process_inputs.values():
            process_input.output = None

        ai_tools = self.ai_tools_in_process()
        for ai_tool in ai_tools:
            ai_tool.output = None
            if isinstance(ai_tool, Process):
                ai_tool.reset_process()

    def can_process(self) -> bool:
        for input in self.process_inputs.values():
            if not input.can_process():
                return False

        return True

    def why_cannot_process(self) -> str:
        for input in self.process_inputs.values():
            if not input.can_process():
                return input.why_cannot_process()

        return f"{self} can process."

    def expose_output(self, tool: AITool) -> "Process":
        if not isinstance(tool, AITool):
            raise TypeError(
                f"Cannot expose output of {self}, because {tool} is not an AITool.")

        self.output_tool = tool
        return self

    def ai_tools_in_process(self) -> List[AITool]:
        # The AI Tools in the process consists of every tool that is connected to the output tool
        # in some way.
        if self.output_tool is None:
            raise AINonRetryableError(
                f"Cannot get AI Tools in process, because {self} does not have an output tool.")

        return list(self._all_connected(self.output_tool))

    def _all_dependents(self, tool: AITool) -> List[AITool]:
        dependents = list()
        for dependent in tool.dependents:
            if isinstance(dependent, _ProcessInput):
                continue
            dependents.append(dependent)
            dependents += self._all_dependents(dependent)
        return dependents

    def _all_dependencies(self, tool: AITool) -> List[AITool]:
        dependencies = list()
        for dependency in tool.dependencies:
            if not isinstance(dependency, _ProcessInput):
                dependencies.append(dependency)
                dependencies += self._all_dependencies(dependency)
        return dependencies

    def _all_connected(self, tool: AITool, seen_tools: Set[AITool] = None) -> Set[AITool]:
        if seen_tools is None:
            seen_tools = set()

        # Add the current tool to the seen_tools set.
        seen_tools.add(tool)

        # Process all dependencies of the tool.
        for dependency in self._all_dependencies(tool):
            if dependency not in seen_tools:
                seen_tools.update(self._all_connected(dependency, seen_tools))

        # Process all dependents of the tool.
        for dependent in self._all_dependents(tool):
            if dependent not in seen_tools:
                seen_tools.update(self._all_connected(dependent, seen_tools))

        return seen_tools


class _ProcessInput(AITool):
    def __init__(self, parent_process: Process):
        super().__init__("ProcessInput")
        self.input_key: str = None
        self.parent_process = parent_process

    def _process(self) -> Any:
        if isinstance(self.input[self.input_key], AITool):
            return self.input[self.input_key]._get_single_output(self)
        return self.input[self.input_key]

    def can_process(self) -> bool:
        if isinstance(self.input[self.input_key], AITool):
            return self.input[self.input_key]._has_single_output(self)
        return True

    def set_input(self, **kwargs) -> "_ProcessInput":
        if len(kwargs) != 1:
            raise ValueError(
                f"Must set input with only one key, not {len(kwargs)}")
        self.input_key = list(kwargs.keys())[0]

        super().set_input(**kwargs)
        return self
