# llm.py

import os
import json
import time
import openai
from openai import OpenAI
import requests
import anthropic
from promptlayer import PromptLayer
from typing import List, Dict, Any
from ai_toolkit import AITool
from ai_toolkit.ai_errors import AINonRetryableError, AIRetryableError


class LLM(AITool):
    """
    LLM is a tool that can be used to call an AI model. It currently supports OpenAI, Anthropics, and Respell models.

    Required inputs:
        model_name: str --- The name of the model to use. Get the list of available models with LLM.ALL_MODEL_NAMES
        prompt: str --- The prompt to send to the model

    Optional inputs:
        max_tokens: int --- The maximum number of tokens to generate
        temperature: float --- The degree of randomness of the model's output; default is 0.5
        max_retries: int --- The maximum number of times to retry the request; default is 5
        response_format: Dict[str, str] --- A dictionary of the response format to use; default is None (to get JSON use {"type": "json_object"})
        use_promptlayer: bool --- Whether to use promptlayer to track the request
        return_pl_id: bool --- Whether to return the promptlayer request id (will return a dict with keys 'response' and 'pl_request_id')
        promptlayer_tags: List[str] --- Tags to add to the promptlayer request

    Dynamic inputs:
        None

    Output:
        Either a string or a dict with keys 'response' and 'pl_request_id'
    """
    OPENAI_MODEL_NAMES = ["gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-4-turbo",
                          "gpt-3.5-turbo-16k", "gpt-4-1106-preview", "gpt-3.5-turbo-1106", "gpt-4-0125-preview", "gpt-3.5-turbo-0125"]
    ANTHROPIC_MODEL_NAMES = ["claude-1", "claude-1-100k",
                             "claude-instant-1", "claude-instant-1-100k", "claude-2"]
    RESPELL_MODEL_NAMES = ["respell-gpt-4-wrapper"]
    ALL_MODEL_NAMES = OPENAI_MODEL_NAMES + \
        ANTHROPIC_MODEL_NAMES + RESPELL_MODEL_NAMES

    def __init__(self, name):
        super().__init__(name)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.respell_api_key = os.getenv("RESPELL_API_KEY")
        self.promptlayer_client = PromptLayer(
            api_key=os.getenv("PROMPTLAYER_API_KEY"))

        self.required_input = ["model_name", "prompt"]
        self.optional_input = ["max_tokens",
                               "temperature", "max_retries", "response_format"]
        self.optional_input.extend([
            "use_promptlayer",
            "return_pl_id",
            "promptlayer_tags"])  # Inputs for tracking the request with promptlayer

        # Default values for optional inputs
        self.set_input(max_tokens=None, temperature=0.5,
                       max_retries=5, response_format=None)

    def _process(self) -> (str | Dict[str, Any]):
        model_name = self._get_from_input("model_name")
        prompt = self._get_from_input("prompt")
        max_tokens = self._get_from_input("max_tokens")
        temperature = self._get_from_input("temperature")
        max_retries = self._get_from_input("max_retries")
        response_format = self._get_from_input("response_format")

        # Promptlayer inputs
        promptlayer_inputs = {
            "use_promptlayer": self._get_from_input("use_promptlayer") if "use_promptlayer" in self.input else False,
            "return_pl_id": self._get_from_input("return_pl_id") if "return_pl_id" in self.input else False,
            "promptlayer_tags": self._get_from_input("promptlayer_tags") if "promptlayer_tags" in self.input else None,
        }

        max_tokens = None if max_tokens is None else int(max_tokens)
        temperature = float(temperature)
        max_retries = 0 if max_retries is None else int(max_retries)

        messages = self._messages_from_text(prompt)
        self._assert_message_formatting(messages)

        retries = 0
        delay = 5
        while retries <= max_retries:
            try:
                if model_name in self.OPENAI_MODEL_NAMES:
                    return self._get_completion_openai(model_name, messages, max_tokens, temperature, response_format, promptlayer_inputs)
                elif model_name in self.ANTHROPIC_MODEL_NAMES:
                    return self._get_completion_anthropic(model_name, messages, max_tokens, promptlayer_inputs)
                elif model_name in self.RESPELL_MODEL_NAMES:
                    return self._get_completion_respell(model_name, messages, promptlayer_inputs, prompt)
                else:
                    raise AINonRetryableError(
                        f"Model name '{model_name}' is not a valid model name. Must be one of {self.ALL_MODEL_NAMES}")
            except AIRetryableError as e:
                retries += 1
                if retries > max_retries:
                    raise AINonRetryableError(
                        f"Error: {e}\tRetried {max_retries} times. Giving up.") from e
                else:
                    print(f"Error: {e}\tRetrying in {delay} seconds...")
                    time.sleep(delay)
                    delay = 10 if delay == 5 else delay + 10
            except AINonRetryableError as e:
                raise e
            except Exception as e:
                raise AINonRetryableError(
                    f"Unknown error occurred: {e}") from e

    @staticmethod
    def _assert_message_formatting(messages: List[Dict[str, str]]):
        prior_role = None
        for message in messages:
            current_role = message["role"]
            if current_role not in ["user", "system", "assistant"]:
                raise AINonRetryableError(
                    f"Message role must be either 'user', 'system', or 'assistant'. Got {current_role}")
            elif prior_role == "system" and current_role not in ["user", "assistant"]:
                raise AINonRetryableError(
                    f"system messages must be followed by a user or assistant message. Got {current_role}")
            elif prior_role == "user" and current_role != "assistant":
                raise AINonRetryableError(
                    f"user messages must be followed by an assistant message. Got {current_role}")
            elif prior_role == "assistant" and current_role != "user":
                raise AINonRetryableError(
                    f"assistant messages must be followed by a user message. Got {current_role}")

            prior_role = current_role

        if prior_role != "user":
            raise AINonRetryableError(
                f"The last message must be a user message. Got {message['role']}")

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

    def _get_completion_openai(self, model_name: str, messages: List[Dict[str, str]], max_tokens: int, temperature: float, response_format: Dict[str, str], promptlayer_inputs) -> str:
        completion_kwargs = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": response_format,
        }
        try:
            if promptlayer_inputs["use_promptlayer"]:
                PLOpenAI = self.promptlayer_client.openai.OpenAI
                client = PLOpenAI(api_key=self.openai_api_key)
                pl_kwargs = self._get_promptlayer_kwargs(promptlayer_inputs)

                response, pl_request_id = client.chat.completions.create(
                    **completion_kwargs,
                    **pl_kwargs
                )

                if promptlayer_inputs["return_pl_id"]:
                    return {"response": response.choices[0].message.content, "pl_request_id": pl_request_id}
            else:
                client = OpenAI(api_key=self.openai_api_key)
                response = client.chat.completions.create(**completion_kwargs)
            return response.choices[0].message.content

        except openai.APITimeoutError as e:
            raise AIRetryableError(
                f"OpenAI API request timed out for model {model_name}: {e}")
        except openai.APIConnectionError as e:
            raise AIRetryableError(
                f"OpenAI API request failed to connect for model {model_name}: {e}")
        except openai.AuthenticationError as e:
            raise AINonRetryableError(
                f"OpenAI API request was not authorized for model {model_name}: {e}")
        except openai.BadRequestError as e:
            raise AINonRetryableError(
                f"OpenAI API request was invalid for model {model_name}: {e}")
        except openai.ConflictError as e:
            raise AIRetryableError(
                f"OpenAI API request conflicted for model {model_name}: {e}")
        except openai.PermissionDeniedError as e:
            raise AINonRetryableError(
                f"OpenAI API request was not permitted for model {model_name}: {e}")
        except openai.RateLimitError as e:
            raise AIRetryableError(
                f"OpenAI API request exceeded rate limit for model {model_name}: {e}")
        except openai.UnprocessableEntityError as e:
            raise AINonRetryableError(
                f"OpenAI API request was unprocessable for model {model_name}: {e}")
        except openai.NotFoundError as e:
            raise AINonRetryableError(
                f"OpenAI API request was not found for model {model_name}: {e}")
        except openai.InternalServerError as e:
            raise AIRetryableError(
                f"OpenAI API request encountered an internal server error for model {model_name}: {e}")

    def _get_completion_anthropic(self, model_name: str, messages: List[Dict[str, str]], max_tokens: int, promptlayer_inputs) -> str:
        prompt = self._create_anthropic_prompt(messages)
        completion_kwargs = {
            "prompt": prompt,
            "model": model_name,
            "max_tokens_to_sample": 4096 if max_tokens is None else max_tokens,
        }

        try:
            if promptlayer_inputs["use_promptlayer"]:
                pl_kwargs = self._get_promptlayer_kwargs(promptlayer_inputs)

                anthropic_client = self.promptlayer_client.anthropic.Anthropic(
                    api_key=self.anthropic_api_key, max_retries=0)
                response, pl_request_id = anthropic_client.completions.create(
                    **completion_kwargs,
                    **pl_kwargs
                )

                if promptlayer_inputs["return_pl_id"]:
                    return {"response": response.completion, "pl_request_id": pl_request_id}
            else:
                anthropic_client = anthropic.Anthropic(
                    api_key=self.anthropic_api_key, max_retries=0)
                response = anthropic_client.completions.create(
                    **completion_kwargs)

            return response.completion

        except anthropic.APIConnectionError as e:
            raise AIRetryableError(
                "The server could not be reached") from e.__cause__
        except anthropic.RateLimitError as e:
            raise AIRetryableError(
                "A 429 status code was received; consider backing off or retrying later.") from e
        except anthropic.AuthenticationError as e:
            raise AINonRetryableError(
                "Invalid API credentials provided.") from e
        except anthropic.PermissionDeniedError as e:
            raise AINonRetryableError(
                "Permission denied for the API request.") from e
        except anthropic.NotFoundError as e:
            raise AIRetryableError(f"Resource not found: {e.response}") from e
        except anthropic.UnprocessableEntityError as e:
            raise AINonRetryableError(
                f"Request could not be processed: {e.response}") from e
        except anthropic.InternalServerError as e:
            raise AIRetryableError(
                f"Internal server error: {e.response}") from e
        except anthropic.APIStatusError as e:
            raise AIRetryableError(
                f"Received a non-200-range status code: {e.status_code}. Response: {e.response}") from e

    def _get_completion_respell(self, model_name: str, messages: List[Dict[str, str]], promptlayer_inputs, original_prompt) -> str:
        request_start_time = time.time()
        instruction, prompt = self._create_respell_prompt(messages)
        completion = self._call_respell_api(model_name, instruction, prompt)

        if promptlayer_inputs["use_promptlayer"]:
            url = "http://api.promptlayer.com/track-request"
            headers = {
                "Content-Type": "application/json",
            }
            data_payload = {
                "function_name": "respell.ai",
                "kwargs": {
                    "prompt": original_prompt,
                },
                "request_response": {
                    "output": completion,
                },
                "tags": promptlayer_inputs.get("promptlayer_tags"),
                "request_start_time": request_start_time,
                "request_end_time": time.time(),
                "api_key": self.promptlayer_api_key,
            }

            pl_response = requests.post(
                url, json=data_payload, headers=headers)
            pl_request_id = pl_response.json()['request_id']

            if promptlayer_inputs["return_pl_id"]:
                return {"response": completion, "pl_request_id": pl_request_id}

        return completion

    @staticmethod
    def _create_anthropic_prompt(messages: List[Dict[str, str]]) -> str:
        prompt = ""
        if messages[0]["role"] == "system":
            message = messages.pop(0)
            prompt += f"\n\nHuman: {message['content']}\n\nAssistant: I understand these instructions."
        for i, message in enumerate(messages):
            # If last message then add '\n\nAssistant:' at the end
            if i == len(messages) - 1:
                prompt += f"\n\nHuman: {message['content']}\n\nAssistant:"
            elif message["role"] == "user":
                prompt += f"\n\nHuman: {message['content']}"
            elif message["role"] == "assistant":
                prompt += f"\n\nAssistant: {message['content']}"

        return prompt

    @staticmethod
    def _create_respell_prompt(messages: List[Dict[str, str]]) -> (str, str):
        instruction = ""
        if messages[0]["role"] == "system":
            instruction = messages[0]["content"]
            messages = messages[1:]
        else:
            instruction = "You are a helpful AI assistant."

        prompt = ""
        for i, message in enumerate(messages):
            # If last message then add '\n\nAssistant: ' at the end
            if i == len(messages) - 1:
                prompt += f"\n\nHuman: {message['content']}\n\nAssistant: "
            elif message["role"] == "user":
                prompt += f"\n\nHuman: {message['content']}"
            elif message["role"] == "assistant":
                prompt += f"\n\nAssistant: {message['content']}"

        return instruction, prompt

    def _call_respell_api(self, model_name: str, instruction: str, prompt: str) -> str:
        models = {
            "respell-gpt-4-wrapper": {
                "spellId": "6fc_quNWYHRVNvfvb53uk",
                "spellVersionId": "TF2mP48JHyO9zQlqVYWMs"
            }
        }

        try:
            response = requests.post(
                "https://api.respell.ai/v1/run",
                headers={
                    'Authorization': f'Bearer {self.respell_api_key}',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                data=json.dumps({
                    "spellId": models[model_name]["spellId"],
                    # This field can be omitted to run the latest published version
                    "spellVersionId": models[model_name]["spellVersionId"],
                    "inputs": {
                        "instruction": instruction,
                        "message": prompt,
                    }
                }),
            )
            # Raise an HTTPError if the response contains a 4xx/5xx status code
            response.raise_for_status()
            completion = response.json()['outputs']['output']
            assert completion is not None

        except requests.ConnectionError:
            raise AIRetryableError(
                "Error in get_completion_respell: Connection error")
        except requests.Timeout:
            raise AIRetryableError(
                "Error in get_completion_respell: Request timed out")
        except requests.RequestException as e:
            raise AIRetryableError(
                f"Error in get_completion_respell: {e}\nStatus code: {response.status_code}\nResponse: {response.text}") from e
        except KeyError as e:
            raise AIRetryableError(
                f"Error in get_completion_respell: {e}\nStatus code: {response.status_code}\nResponse: {response.text}") from e
        except AssertionError as e:
            raise AIRetryableError(
                f"Received None response in get_completion_respell\n{e}\n{response}\n{response.json()}") from e

        return completion

    @staticmethod
    def _get_promptlayer_kwargs(promptlayer_inputs: Dict[str, Any]) -> Dict[str, Any]:
        promptlayer_kwargs = {
            "return_pl_id": True,
            "pl_tags": promptlayer_inputs.get("promptlayer_tags"),
        }

        return {k: v for k, v in promptlayer_kwargs.items() if v is not None}
