# model_respell.py

import os
import requests
import json
from .base import AIModel
from typing import List, Dict

class ModelRespell(AIModel):
    MODEL_NAMES = ["respell-gpt-4-wrapper"]

    def __init__(self, model_name: str, **kwargs):
        super().__init__(model_name, **kwargs)
        self.respell_api_key = os.getenv("RESPELL_API_KEY")

    def get_completion(self, messages: list[dict]) -> str:
        self._assert_message_formatting(messages)
        instruction = ""
        if messages[0]["role"] == "system":
            instruction = messages[0]["content"]
            messages = messages[1:]
        
        prompt = ""
        for i, message in enumerate(messages):
            # If last message then add '\n\nAssistant: ' at the end
            if i == len(messages) - 1:
                prompt += f"\n\Human: {message['content']}\n\nAssistant: "
            elif message["role"] == "user":
                prompt += f"\n\Human: {message['content']}"
            elif message["role"] == "assistant":
                prompt += f"\n\nAssistant: {message['content']}"

        response = requests.post(
        "https://api.respell.ai/v1/run",
        headers={
            # This is your API key
            'Authorization': f'Bearer {self.respell_api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        data=json.dumps({
            "spellId": "6fc_quNWYHRVNvfvb53uk",
            # This field can be omitted to run the latest published version
            "spellVersionId": 'TF2mP48JHyO9zQlqVYWMs',
            # Fill in dynamic values for each of your 2 input blocks
            "inputs": {
                "instruction": instruction,
                "message": prompt,
            }
        }),
        )
        try:
            analysis = response.json()['outputs']['output']
            assert analysis is not None
            return analysis
        except Exception as e:
            self.logger.error(f"Error in get_completion_respell\n{e}\n{response}\n{response.json()}")
            raise e

    # TODO: Implement these methods
    def get_prompt(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError

    def get_num_tokens(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError
