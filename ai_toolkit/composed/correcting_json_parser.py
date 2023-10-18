# correcting_json_parser.py

import json
from ai_toolkit import AITool, CustomCodeBlock
from ai_toolkit.ai_errors import AINonRetryableError, AIRetryableError
from ai_toolkit.flow import Process, Conditional
from ai_toolkit.tools import PromptBuilder, LLM
from ai_toolkit.operations import Passthrough, ConvertToJSON, ExtractKey
from ai_toolkit.composed.llm_with_prompt_retrieval_and_tracking import LLMWithPromptRetrievalAndTracking


class CanConvertToJSON(CustomCodeBlock):
    def code(self):
        input = self.get_input("json_string")
        if not isinstance(input, str):
            raise AINonRetryableError(
                f"Input must be of type str, not {type(input).__name__}")
        try:
            json.loads(input)
            return {"can_convert": True, "error_message": ""}
        except json.decoder.JSONDecodeError as e:
            return {"can_convert": False, "error_message": str(e)}


class CreateReplacements(CustomCodeBlock):
    def code(self):
        json_string = self.get_input("json_string")
        error_message = self.get_input("error_message")

        return {
            "json_string": json_string,
            "error_message": error_message
        }


def CorrectingJSONParser(name: str) -> Process:
    """
    This process takes a JSON string, parses it, and if it fails, it tries to fix it and parse it again.

    Required input:
        json_string: str --- The JSON string to parse
        promptlayer_tags: List[str] --- A list of tags to associate with the prompt
        model_name: str --- The name of the LLM to call
        metadata: Dict[str, Any] --- A dictionary of metadata to track with the prompt
    """
    # Create the input to the overall process
    json_string = Passthrough(name).set_input(
        name_of_input="json_string")

    # Create the input to the conditional
    can_convert_to_json = CanConvertToJSON(name).set_input(
        json_string=json_string)

    can_convert_bool = ExtractKey(f"{name} - Can Convert Bool").set_input(
        input=can_convert_to_json,
        key_name="can_convert")

    error_message = ExtractKey(f"{name} - Error Message").set_input(
        input=can_convert_to_json,
        key_name="error_message")

    # Tools in the true path
    convert_to_json_on_true = ConvertToJSON(name)

    # Tools in the false path
    json_string_input = Passthrough(name).set_input(
        name_of_input="input")

    replacements_for_llm = CreateReplacements(name).set_input(
        json_string=json_string_input)

    llm_json_fixer = LLMWithPromptRetrievalAndTracking(name).set_input(
        template_name="JSON Fixer",
        replacements=replacements_for_llm,)

    convert_to_json_after_fixed = ConvertToJSON(name).set_input(
        input=llm_json_fixer)

    # Create the conditional
    json_fixer_conditional = Conditional(name).set_input(
        condition=can_convert_bool,
        error_message=error_message,
        input=json_string,)

    json_fixer_conditional.expose_input("input", convert_to_json_on_true)
    json_fixer_conditional.expose_input("input", json_string_input)
    json_fixer_conditional.expose_input("error_message", replacements_for_llm)
    json_fixer_conditional.expose_input("promptlayer_tags", llm_json_fixer)
    json_fixer_conditional.expose_input("model_name", llm_json_fixer)
    json_fixer_conditional.expose_input("metadata", llm_json_fixer)
    json_fixer_conditional.expose_output(
        tool_if_true=convert_to_json_on_true,
        tool_if_false=convert_to_json_after_fixed)

    # Wrap everything in a process
    correcting_json_parser = Process(name)
    correcting_json_parser.expose_input("json_string", json_string)
    correcting_json_parser.expose_input(
        "promptlayer_tags", json_fixer_conditional)
    correcting_json_parser.expose_input("model_name", json_fixer_conditional)
    correcting_json_parser.expose_input("metadata", json_fixer_conditional)
    correcting_json_parser.expose_output(json_fixer_conditional)

    return correcting_json_parser
