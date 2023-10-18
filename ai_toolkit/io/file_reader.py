# file_reader.py

from ai_toolkit import AITool
from ai_toolkit.ai_errors import AINonRetryableError
from typing import List, Dict, Any
import json


class FileReader(AITool):
    def __init__(self, name):
        super().__init__(name)
        self.required_input = ["file_path"]
        self.optional_input = ["file_encoding"]

        self.set_input(file_encoding="utf-8")

    def _process(self) -> (str | Dict[str, Any]):
        file_path = self._get_from_input("file_path")
        file_encoding = self._get_from_input("file_encoding")

        # Get the file type
        try:
            file_type = file_path.split(".")[-1]
        except IndexError:
            raise AINonRetryableError(
                f"File path '{file_path}' does not contain a file type")

        # Check that the file type is valid
        if file_type not in ["txt", "json"]:
            raise AINonRetryableError(
                f"File type '{file_type}' is not a valid file type, must be 'txt' or 'json'")

        # Read the file
        try:
            switch = {
                "txt": self._read_text_file,
                "json": self._read_json_file
            }
            file_contents = switch[file_type](file_path, file_encoding)
        except FileNotFoundError:
            raise AINonRetryableError(f"File '{file_path}' not found")
        except UnicodeDecodeError:
            raise AINonRetryableError(
                f"File '{file_path}' could not be decoded with encoding '{file_encoding}'")
        except Exception as e:
            raise AINonRetryableError(
                f"Unknown error occurred when reading file '{file_path}': {e}")

        return file_contents

    def _read_text_file(self, file_path, file_encoding) -> str:
        with open(file_path, "r", encoding=file_encoding) as f:
            file_contents = f.read()
        return file_contents

    def _read_json_file(self, file_path, file_encoding) -> Dict[str, Any]:
        with open(file_path, "r", encoding=file_encoding) as f:
            file_contents = json.load(f)
        return file_contents
