# prompt_section.py

from typing import Dict, Any

class PromptSection:
    def __init__(self, prompt_type):
        assert prompt_type in ["system", "user", "assistant"]
        self.prompt_type = prompt_type
        self.prompt = None
    
    def set_prompt(self, prompt: str):
        self.prompt = prompt
        return self
    
    def is_set(self):
        return self.prompt is not None
    
    def build_section(self, replacements: Dict[str, Any]) -> Dict[str, str]:
        content = self.prompt
        for key in replacements:
            content = content.replace("{{" + key + "}}", replacements[key])
        return {
            "role": self.prompt_type,
            "content": content
        }
