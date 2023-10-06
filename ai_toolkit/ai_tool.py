# ai_tool.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .ai_errors import AINonRetryableError, AIRetryableError

class AITool(ABC):
    def __init__(self, name):
        self.name: str = name

        self.input: Dict[str, Any | "AITool"] = dict()
        self.required_input: List[str] = list()
        self.optional_input: List[str] = list()
        self.dynamic_input: List[str] = list()

        self.output: Any = None
        self.dependents_received_output: List["AITool"] = list()

        self.dependencies: List["AITool"] = list()
        self.dependents: List["AITool"] = list()

    def process(self) -> "AITool":
        if not self.can_process():
            raise AINonRetryableError(f"Cannot process {self.__class__.__name__} because not all inputs are present.\n \
                                      Required inputs: {self.required_input}\nDynamic inputs: {self.dynamic_input}")
        
        self.dependents_received_output = list()
        self.output = self._process()
        return self
    
    @abstractmethod
    def _process(self) -> Any:
        raise NotImplementedError
        
    def set_input(self, **kwargs) -> "AITool":
        for key, value in kwargs.items():
            if key not in self.required_input and key not in self.optional_input:
                self.dynamic_input.append(key)

            # If the value is an AITool, add it to the dependencies, and add to the dependents of the AITool
            if isinstance(value, AITool):
                self.dependencies.append(value)
                value._add_dependent(self)

            self.input[key] = value

        return self

    def get_output(self) -> Any:
        return self.output
    
    def can_process(self) -> bool:
        required_inputs = self.required_input + self.dynamic_input
        for key in required_inputs:
            if key not in self.input:
                return False
            
        for input in self.input.values():
            if isinstance(input, AITool) and not input._has_single_output(self):
                return False
            
        return True
    
    def why_cannot_process(self) -> str:
        if self.can_process():
            return f"{self.__class__.__name__} can process."
        
        required_inputs = self.required_input + self.dynamic_input
        missing_inputs = [key for key in required_inputs if key not in self.input]
        if len(missing_inputs) > 0:
            return f"{self.__class__.__name__} cannot process because the following inputs are missing: {missing_inputs}"
        
        for input in self.input.values():
            if isinstance(input, AITool) and not input._has_single_output(self):
                return f"{self.__class__.__name__} cannot process because {input.__class__.__name__} does not have a single output."
        
        return f"{self.__class__.__name__} cannot process for an unknown reason."

    def _get_single_output(self, getter: "AITool") -> Any:
        if not self._has_single_output(getter):
            raise Exception(f"Cannot get single output from {self.__class__.__name__} for {getter.__class__.__name__} because there are no outputs ready.")

        self.dependents_received_output.append(getter)
        return self.output
    
    def _get_from_input(self, key: str) -> Any:
        if key not in self.input:
            raise KeyError(f"Input '{key}' not found in {self.__class__.__name__}")
        
        if isinstance(self.input[key], AITool):
            value = self.input[key]._get_single_output(self)
        else:
            value = self.input[key]

        return value
    
    def _has_single_output(self, getter: "AITool") -> bool:
        if getter not in self.dependents_received_output and self.output is not None:
            return True
        return False
    
    def _add_dependent(self, dependent: "AITool") -> "AITool":
        self.dependents.append(dependent)
        return self
    
    def _has_inputs_connected(self) -> bool:
        for key in self.required_input:
            if key not in self.input:
                return False
        return True
    
    def __repr__(self) -> str:
        return f"{self.name} ({self.__class__.__name__})"
    
    