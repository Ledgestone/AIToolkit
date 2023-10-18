# file_writer.py

from ai_toolkit import AITool
from ai_toolkit.ai_errors import AINonRetryableError
from typing import List, Dict, Any
import json


class FileWriter(AITool):
    def __init__(self, name):
        super().__init__(name)
        self.required_input = ["file_path", "data"]
        self.optional_input = ["file_encoding"]

        self.set_input(file_encoding="utf-8")

    def _process(self) -> str:
        file_path = self._get_from_input("file_path")
        file_encoding = self._get_from_input("file_encoding")
        data = self._get_from_input("data")

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

        # Write to the file
        try:
            switch = {
                "txt": self._write_text_file,
                "json": self._write_json_file
            }
            switch[file_type](file_path, file_encoding, data)
        except UnicodeEncodeError:
            raise AINonRetryableError(
                f"File '{file_path}' could not be encoded with encoding '{file_encoding}'")
        except Exception as e:
            raise AINonRetryableError(
                f"Unknown error occurred when writing to file '{file_path}': {e}")

        return "File successfully written"

    def _write_text_file(self, file_path, file_encoding, data) -> None:
        with open(file_path, "w", encoding=file_encoding) as f:
            f.write(data)

    def _write_json_file(self, file_path, file_encoding, data) -> None:
        with open(file_path, "w", encoding=file_encoding) as f:
            json.dump(data, f)
