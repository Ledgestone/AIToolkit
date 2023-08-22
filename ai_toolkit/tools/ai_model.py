# base.py

import os
import json
import openai
import requests
from typing import List, Dict
from ..ai_tool import AITool
from ..ai_errors import AINonRetryableError, AIRetryableError


class AIModel(AITool):
    OPENAI_MODEL_NAMES = ["gpt-3.5-turbo", "gpt-4", "gpt-3.5-turbo-16k"]
    ANTHROPIC_MODEL_NAMES = ["claude-1", "claude-1-100k", "claude-instant-1", "claude-instant-1-100k"]
    RESPELL_MODEL_NAMES = ["respell-gpt-4-wrapper"]
    ALL_MODEL_NAMES = OPENAI_MODEL_NAMES + ANTHROPIC_MODEL_NAMES + RESPELL_MODEL_NAMES

    def __init__(self, name):
        super().__init__(name)        
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.respell_api_key = os.getenv("RESPELL_API_KEY")
        
        self.required_input = ["model_name", "prompt"]
        self.optional_input = ["max_tokens", "temperature"]

        self.set_input(max_tokens="None", temperature="0.5")

    def _process(self) -> str:
        model_name = self._get_from_input("model_name")
        prompt = self._get_from_input("prompt")
        max_tokens = self._get_from_input("max_tokens")
        temperature = self._get_from_input("temperature")

        if max_tokens == "None":
            max_tokens = None
        else:
            max_tokens = int(max_tokens)
        temperature = float(temperature)

        messages = self._messages_from_text(prompt)
        self._assert_message_formatting(messages)

        if model_name in self.OPENAI_MODEL_NAMES:
            return self._get_completion_openai(model_name, messages, max_tokens, temperature)
        elif model_name in self.ANTHROPIC_MODEL_NAMES:
            return self._get_completion_anthropic(model_name, messages, max_tokens)
        elif model_name in self.RESPELL_MODEL_NAMES:
            return self._get_completion_respell(model_name, messages)
        else:
            raise AINonRetryableError(f"Model name '{model_name}' is not a valid model name. Must be one of {self.ALL_MODEL_NAMES}")
    
    @staticmethod
    def _assert_message_formatting(messages: List[Dict[str, str]]):
        prior_role = None
        for message in messages:
            current_role = message["role"]
            if current_role not in ["user", "system", "assistant"]:
                raise AINonRetryableError(f"Message role must be either 'user', 'system', or 'assistant'. Got {current_role}")
            elif prior_role == "system" and current_role not in ["user", "assistant"]:
                raise AINonRetryableError(f"system messages must be followed by a user or assistant message. Got {current_role}")
            elif prior_role == "user" and current_role != "assistant":
                raise AINonRetryableError(f"user messages must be followed by an assistant message. Got {current_role}")
            elif prior_role == "assistant" and current_role != "user":
                raise AINonRetryableError(f"assistant messages must be followed by a user message. Got {current_role}")

            prior_role = current_role

        if prior_role != "user":
            raise AINonRetryableError(f"The last message must be a user message. Got {message['role']}")

    @staticmethod
    def _messages_from_text(text: str) -> List[Dict[str, str]]:
        lines = text.split('\n')
        output = []
        current_role = None
        message_lines = []

        for line in lines:
            if line.rstrip().endswith(':') and line.rstrip(': ').lower().strip() in ['user', 'system', 'assistant']:
                if current_role is not None and message_lines:
                    message = '\n'.join(message_lines).strip()
                    output.append({'role': current_role, 'content': message})
                current_role = line.rstrip(': ').lower().strip()
                message_lines = []
            else:
                message_lines.append(line)

        # Add the last message
        if current_role is not None and message_lines: 
            message = '\n'.join(message_lines).strip()
            output.append({'role': current_role, 'content': message})

        # Handle input where no role is specified
        if current_role is None:
            message = '\n'.join(message_lines).strip()
            output = [{'role': 'user', 'content': message}]

        return output
    
    def _get_completion_openai(self, model_name: str, messages: List[Dict[str, str]], max_tokens: int, temperature: float) -> str:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            temperature=temperature, # this is the degree of randomness of the model's output
            max_tokens=max_tokens, # this is the maximum number of tokens to generate
        )
        return response.choices[0].message["content"]
    
    def _get_completion_anthropic(self, model_name: str, messages: List[Dict[str, str]], max_tokens: int) -> str:
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
            "model": model_name,
            "prompt": prompt,
            "max_tokens_to_sample": 4096 if max_tokens is None else max_tokens,
        }

        response = requests.post(url, json=data, headers=headers)
        return response.json()
    
    def _get_completion_respell(self, model_name: str, messages: List[Dict[str, str]]) -> str:
        models = {
            "respell-gpt-4-wrapper": {
                "spellId": "6fc_quNWYHRVNvfvb53uk", 
                "spellVersionId": "TF2mP48JHyO9zQlqVYWMs"
            }
        }

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

        try:
            response = requests.post(
            "https://api.respell.ai/v1/run",
            headers={
                # This is your API key
                'Authorization': f'Bearer {self.respell_api_key}',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                "spellId": models[model_name]["spellId"],
                # This field can be omitted to run the latest published version
                "spellVersionId": models[model_name]["spellVersionId"],
                # Fill in dynamic values for each of your 2 input blocks
                "inputs": {
                    "instruction": instruction,
                    "message": prompt,
                }
            }),
            )

            analysis = response.json()['outputs']['output']
            assert analysis is not None
            return analysis
        except Exception as e:
            raise AIRetryableError(f"Error in get_completion_respell\n{e}\n{response}\n{response.json()}") from e

