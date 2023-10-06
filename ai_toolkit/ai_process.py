# ai_process.py

from ai_toolkit.ai_tool import AITool
from typing import List, Dict, Any
from ai_toolkit.ai_errors import AINonRetryableError, AIRetryableError

class AIProcess(AITool):
    def __init__(self, name):
        super().__init__(name)
        self.output_tool: AITool = None
        self.process_inputs: Dict[str, "_AIProcessInput"] = dict()
    
    def _process(self) ->  Any:
        ai_tools = self.ai_tools_in_process()
        for ai_tool in ai_tools:
            if not ai_tool._has_inputs_connected():
                raise AINonRetryableError(f"Cannot process {self}, because {ai_tool} does not have all its required inputs connected.")
            
        for process_input in self.process_inputs.values():
            process_input.process()

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
            unpocessed_tools = [ai_tool for ai_tool in ai_tools if ai_tool not in processed_tools]
            raise AIRetryableError(f"Cannot finish processing {self}, because the following tools could not be processed: {unpocessed_tools}")
        
        return self.output_tool.get_output()
    
    def set_input(self, **kwargs) -> "AIProcess":
        for key, value in kwargs.items():
            if key in self.process_inputs:
                self.process_inputs[key].set_input(**{key: value})
            else:
                self.process_inputs[key] = _AIProcessInput(self).set_input(**{key: value})
                self.dynamic_input.append(key)

            # If the value is an AITool, add it to the dependencies, and add to the dependents of the AITool
            if isinstance(value, AITool):
                self.dependencies.append(value)
                value._add_dependent(self)

            self.input[key] = value
        
        return self
    
    def expose_input(self, key: str, tool: AITool) -> "AIProcess":
        if key in self.process_inputs:
            tool.set_input(**{key: self.process_inputs[key]})
        else:
            self.process_inputs[key] = _AIProcessInput(self)
            tool.set_input(**{key: self.process_inputs[key]})
            self.dynamic_input.append(key)

        return self
    
    def can_process(self) -> bool:
        for input in self.process_inputs.values():
            if not input.can_process():
                return False
        
        return True
            
    def why_cannot_process(self) -> str:
        for input in self.process_inputs.values():
            if not input.can_process():
                return input.why_cannot_process()
            
        return f"{self.__class__.__name__} can process."
    
    def expose_output(self, tool: AITool) -> "AIProcess":
        self.output_tool = tool
        return self
    
    def ai_tools_in_process(self) -> List[AITool]:
        # The AI Tools in the process are just all the dependents of the inputs and all
        # the dependencies of the output tool
        ai_tools = list()
        for process_input in self.process_inputs.values():
            for dependent in self._all_dependents(process_input):
                if dependent not in ai_tools:
                    ai_tools.append(dependent)
        if self.output_tool is not None:
            for dependency in self._all_dependencies(self.output_tool):
                if dependency not in ai_tools:
                    ai_tools.append(dependency)
        return ai_tools
    
    def _all_dependents(self, tool: AITool) -> List[AITool]:
        dependents = list()
        for dependent in tool.dependents:
            if isinstance(dependent, _AIProcessInput):
                continue
            dependents.append(dependent)
            dependents += self._all_dependents(dependent)
        return dependents
    
    def _all_dependencies(self, tool: AITool) -> List[AITool]:
        dependencies = list()
        for dependency in tool.dependencies:
            if not isinstance(dependency, _AIProcessInput):
                dependencies.append(dependency)
                dependencies += self._all_dependencies(dependency)
        return dependencies
    
    
class _AIProcessInput(AITool):
    def __init__(self, parent_process: AIProcess):
        super().__init__("AIProcessInput")
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
    
    def set_input(self, **kwargs) -> "_AIProcessInput":
        if len(kwargs) != 1:
            raise ValueError(f"Must set input with only one key, not {len(kwargs)}")
        self.input_key = list(kwargs.keys())[0]
        
        super().set_input(**kwargs)
        return self
