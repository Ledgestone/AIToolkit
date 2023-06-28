# base.py

from abc import ABC, abstractmethod
import logging
from typing import List, Dict


class AIModel(ABC):
    def __init__(self, model_name: str, **kwargs):
        if self.MODEL_NAMES is None:
            raise NotImplementedError("Subclasses must define MODEL_NAMES class variable with valid model names.")
        
        self.model_name = model_name
        self.max_tokens = kwargs.get("max_tokens", None)
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def get_completion(self, messages: List[Dict[str, str]]) -> str:
        """
        Get the LLM completion for the given messages.

        Usage Example:
        ```python
        messages = [{"role": "user", "content": "What is the capital of France?"}]
        ai_model.get_completion(messages)
        ```

        Args:
            messages (List[Dict[str, str]]): List of messages.
        
        Returns:
            str: The completion for the given messages.
        """
        raise NotImplementedError

    @abstractmethod
    def get_prompt(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_num_tokens(self, messages: List[Dict[str, str]]) -> str:
        """
        Get the number of tokens in the prompt for the given messages. Note that depending on the model being used,
        there may be small variations in the number of tokens returned for the same messages.

        Args:
            messages (List[Dict[str, str]]): List of messages.
        
        Returns:
            str: The number of tokens in the prompt for the given messages.
        """
        raise NotImplementedError
    
    @staticmethod
    def _assert_message_formatting(messages: list[dict]):
        prior_role = None
        for message in messages:
            current_role = message["role"]
            if prior_role is None:
                if current_role not in ["user", "system"]:
                    raise AssertionError(f"The first role must be either 'user' or 'system'. Got {current_role}")
            elif prior_role == "system" and current_role != "user":
                raise AssertionError(f"system messages must be followed by a user message. Got {current_role}")
            elif prior_role == "user" and current_role != "assistant":
                raise AssertionError(f"user messages must be followed by an assistant message. Got {current_role}")
            elif prior_role == "assistant" and current_role != "user":
                raise AssertionError(f"assistant messages must be followed by a user message. Got {current_role}")

            if current_role not in ["user", "system", "assistant"]:
                raise AssertionError(f"Message role must be either 'user', 'system', or 'assistant'. Got {current_role}")

            prior_role = current_role

        if prior_role != "user":
            raise AssertionError(f"The last message must be a user message. Got {message['role']}")
