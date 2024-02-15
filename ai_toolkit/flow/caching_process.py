# caching_process.py

from typing import Any
from ai_toolkit.flow.process import Process
import json
import hashlib


class CachingProcess(Process):
    def __init__(self, name):
        super().__init__(name)
        self.cache = {}

    def _process(self) -> Any:
        self._process_all_inputs()

        inputs = dict()
        for key, process_input in self.process_inputs.items():
            inputs[key] = process_input.get_output()

        cache_key = self._hash_with_json(inputs)
        if cache_key in self.cache:
            return self.cache[cache_key]

        self._process_all_tools()
        output = self.output_tool.get_output()

        self.cache[cache_key] = output
        return output

    @staticmethod
    def _hash_with_json(obj):
        json_string = json.dumps(obj, sort_keys=True)
        return hashlib.sha256(json_string.encode()).hexdigest()
