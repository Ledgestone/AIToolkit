# promptlayer.py

import os
from ..ai_tool import AITool
from ..ai_errors import AINonRetryableError
from typing import List, Dict, Any
import promptlayer

class PromptLayerRegistry(AITool):
    def __init__(self, name):
        super().__init__(name)
        promptlayer.api_key = os.getenv("PROMPTLAYER_API_KEY")
        self.required_input = ["template_name"]
        self.optional_input = ["template_label", "template_version"]

    def _process(self) -> str:
        template_name = self._get_from_input("template_name")

        additional_keys = {
            "template_label": self._get_from_input("template_label") if "template_label" in self.input else None,
            "template_version": self._get_from_input("template_version") if "template_version" in self.input else None
        }

        try:
            template = promptlayer.prompts.get(template_name, **{k: v for k, v in additional_keys.items() if v is not None}).get("template")
        except Exception as e:
            raise AINonRetryableError(f"Error getting prompt template: '{e}'")
        
        return template
    
class PromptLayerPromptTracker(AITool):
    def __init__(self, name):
        super().__init__(name)
        promptlayer.api_key = os.getenv("PROMPTLAYER_API_KEY")
        self.required_input = ["pl_request_id", "template_name", "prompt_input_variables"]
        self.optional_input = ["template_version", "template_version"]

    def _process(self) -> str:
        pl_request_id = self._get_from_input("pl_request_id")
        template_name = self._get_from_input("template_name")
        prompt_input_variables = self._get_from_input("prompt_input_variables")

        additional_keys = {
            "template_label": self._get_from_input("template_label") if "template_label" in self.input else None,
            "template_version": self._get_from_input("template_version") if "template_version" in self.input else None
        }

        try:
            prompt = promptlayer.track.prompt(pl_request_id, template_name, prompt_input_variables, 
                                              **{k: v for k, v in additional_keys.items() if v is not None})
        except Exception as e:
            raise AINonRetryableError(f"Error getting prompt: '{e}'")
        
        return prompt
    
class PromptLayerGroupCreator(AITool):
    def __init__(self, name):
        super().__init__(name)
        promptlayer.api_key = os.getenv("PROMPTLAYER_API_KEY")
        self.required_input = []

    def _process(self) -> str:
        try:
            group = promptlayer.group.create()
        except Exception as e:
            raise AINonRetryableError(f"Error creating group: '{e}'")
        
        return group
    
class PromptLayerGroupTracker(AITool):
    def __init__(self, name):
        super().__init__(name)
        promptlayer.api_key = os.getenv("PROMPTLAYER_API_KEY")
        self.required_input = ["pl_request_id", "pl_group_id"]

    def _process(self) -> str:
        pl_request_id = self._get_from_input("pl_request_id")
        group_id = self._get_from_input("group_id")

        try:
            group = promptlayer.track.group(pl_request_id, group_id)
        except Exception as e:
            raise AINonRetryableError(f"Error getting group: '{e}'")
        
        return group
    
class PromptLayerMetadataTracker(AITool):
    def __init__(self, name):
        super().__init__(name)
        promptlayer.api_key = os.getenv("PROMPTLAYER_API_KEY")
        self.required_input = ["pl_request_id", "metadata"]

    def _process(self) -> str:
        pl_request_id = self._get_from_input("pl_request_id")
        metadata = self._get_from_input("metadata")

        try:
            metadata = promptlayer.track.metadata(pl_request_id, metadata)
        except Exception as e:
            raise AINonRetryableError(f"Error getting metadata: '{e}'")
        
        return metadata



        

        



    