# ai_custom_code.py

import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ai_toolkit.ai_tool import AITool
from ai_toolkit.ai_errors import AINonRetryableError, AIRetryableError

class CustomCodeBlock(AITool, ABC):
    def __init__(self, name):
        super().__init__(name)
    
    def _process(self) -> Any:
        try:
            return self.code()
        except Exception as e:
            raise AINonRetryableError(f"Error trying to execute custom code\nError: {e}")
    
    def get_input(self, key: str) -> str | Dict[str, Any]:
        return self._get_from_input(key)
    
    @abstractmethod
    def code(self) -> Any:
        raise NotImplementedError
