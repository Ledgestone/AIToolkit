# api_request.py

import json
import requests
from typing import List, Dict, Any
from ..ai_tool import AITool
from ..ai_errors import AINonRetryableError, AIRetryableError

class APIRequest(AITool):
    def __init__(self, name):
        super().__init__(name)
        self.required_input = ["url", "method"]
        self.optional_input = ["headers", "body", "params", "auth", "json", "timeout"]

    def _process(self) -> Any:
        url = self._get_from_input("url")
        method = self._get_from_input("method")
        headers = self._get_from_input("headers") if "headers" in self.input else None
        body = self._get_from_input("body") if "body" in self.input else None
        params = self._get_from_input("params") if "params" in self.input else None
        auth = self._get_from_input("auth") if "auth" in self.input else None
        json = self._get_from_input("json") if "json" in self.input else None
        timeout = self._get_from_input("timeout") if "timeout" in self.input else None

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params, auth=auth, timeout=timeout)
            elif method == "POST":
                response = requests.post(url, headers=headers, data=body, params=params, auth=auth, json=json, timeout=timeout)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, data=body, params=params, auth=auth, json=json, timeout=timeout)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, data=body, params=params, auth=auth, json=json, timeout=timeout)
            else:
                raise AINonRetryableError(f"Method '{method}' not supported")
        except requests.exceptions.Timeout:
            raise AIRetryableError(f"Request timed out")
        except requests.exceptions.ConnectionError:
            raise AIRetryableError(f"Connection error")
        except requests.exceptions.HTTPError:
            raise AIRetryableError(f"HTTP error")
        except requests.exceptions.TooManyRedirects:
            raise AIRetryableError(f"Too many redirects")
        except requests.exceptions.RequestException:
            raise AIRetryableError(f"Request exception")

        return response.json()