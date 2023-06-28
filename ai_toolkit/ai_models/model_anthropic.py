# model_anthropic.py

import os
import requests
from .base import AIModel
from typing import List, Dict

class ModelAnthropic(AIModel):
    MODEL_NAMES = ["claude-1", "claude-1-100k", "claude-instant-1", "claude-instant-1-100k"]

    def __init__(self, model_name: str, **kwargs):
        super().__init__(model_name, **kwargs)
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    def get_completion(self, messages: list[dict]) -> str:
        self._assert_message_formatting(messages)
        prompt = ""
        if messages[0]["role"] == "system":
            prompt += f"\n\Human: {message['content']}\n\nAssistant: I understand these instructions."
        for i, message in enumerate(messages):
            # If last message then add '\n\nAssistant: ' at the end
            if i == len(messages) - 1:
                prompt += f"\n\Human: {message['content']}\n\nAssistant: "
            elif message["role"] == "user":
                prompt += f"\n\Human: {message['content']}"
            elif message["role"] == "assistant":
                prompt += f"\n\nAssistant: {message['content']}"


        url = "https://api.anthropic.com/v1/complete"
        headers = {
            "accept": "application/json",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "x-api-key": self.anthropic_api_key,
        }
        data = {
            "model": self.model_name,
            "prompt": f"\n\nuser: {prompt}\n\nassistant:",
            "max_tokens_to_sample": 4096 if self.max_tokens is None else self.max_tokens,
        }

        response = requests.post(url, json=data, headers=headers)
        return response.json()

    # TODO: Implement these methods
    def get_prompt(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError

    def get_num_tokens(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError
