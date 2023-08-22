# prompt_builder.py

from ..ai_tool import AITool
from ..ai_errors import AINonRetryableError
from typing import List, Dict, Any

class PromptBuilder(AITool):
    def __init__(self, name):
        super().__init__(name)
        self.required_input = ["template"]

    def _process(self) -> str:
        template = self._get_from_input("template")

        # Find all keys in the template (denoted by {{key}})
        keys = []
        for i in range(len(template)):
            if template[i] == "{" and template[i+1] == "{":
                key = ""
                i += 2
                while template[i] != "}":
                    key += template[i]
                    i += 1
                keys.append(key)

        # Get the values for each key
        replacements = dict()
        for key in keys:
            try:
                value = self._get_from_input(key)
            except KeyError:
                raise AINonRetryableError(f"Key '{key}' not found in input")
            replacements[key] = value

        # Replace the keys with the values
        prompt = template
        for key, value in replacements.items():
            if not isinstance(value, str):
                raise AINonRetryableError(f"Value for key '{key}' must be of type str, not {type(value).__name__}")
            prompt = prompt.replace("{{" + key + "}}", value)

        return prompt

        



    