# model_openai.py

import os
import openai
from .base import AIModel
from typing import List, Dict

class ModelOpenAI(AIModel):
    MODEL_NAMES = ["gpt-3.5-turbo", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k"]

    def __init__(self, model_name: str, **kwargs):
        super().__init__(model_name, **kwargs)
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.temperature = kwargs.get("temperature", 0.5)

    def get_completion(self, messages: list[dict]) -> str:
        self._assert_message_formatting(messages)
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature, # this is the degree of randomness of the model's output
            max_tokens=self.max_tokens, # this is the maximum number of tokens to generate
        )
        return response.choices[0].message["content"]

    # TODO: Implement these methods
    def get_prompt(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError

    def get_num_tokens(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError
