# llm_with_prompt_retrieval_and_tracking.py

from ai_toolkit import AITool
from ai_toolkit.flow import Process
from ai_toolkit.tools import PromptBuilder, LLM
from ai_toolkit.io.promptlayer_tools import PromptLayerPromptTracker, PromptLayerRegistry, PromptLayerMetadataTracker
from ai_toolkit.operations import Passthrough, ExtractKey


def LLMWithPromptRetrievalAndTracking(name: str) -> Process:
    """
    This process retrieves a prompt from the PromptLayer Registry, fills in the keys with replacements, calls an LLM with that prompt, and then tracks the prompt using PromptLayer

    Required input:
        template_name: str --- The name of the template to retrieve from the PromptLayer Registry
        promptlayer_tags: List[str] --- A list of tags to associate with the prompt
        replacements: Dict[str, str] --- A dictionary of replacements for the template
        model_name: str --- The name of the LLM to call
        metadata: Dict[str, Any] --- A dictionary of metadata to track with the prompt
    """
    prompt_registry = PromptLayerRegistry(name)

    replacements_passthrough = Passthrough(name).set_input(
        name_of_input="replacements")

    prompt_builder = PromptBuilder(name).set_input(
        template=prompt_registry)

    llm = LLM(name).set_input(
        prompt=prompt_builder,
        use_promptlayer=True,
        return_pl_id=True)

    promptlayer_request_id = ExtractKey(name).set_input(
        input=llm,
        key_name="pl_request_id")

    llm_response = ExtractKey(name).set_input(
        input=llm,
        key_name="response")

    prompt_tracker = PromptLayerPromptTracker(name).set_input(
        pl_request_id=promptlayer_request_id,
        prompt_input_variables=replacements_passthrough)

    metadata_tracker = PromptLayerMetadataTracker(name).set_input(
        pl_request_id=promptlayer_request_id)

    prompt_and_llm = Process(name)
    prompt_and_llm.expose_input("template_name", prompt_registry)
    prompt_and_llm.expose_input("template_name", prompt_tracker)
    prompt_and_llm.expose_input("promptlayer_tags", llm)
    prompt_and_llm.expose_input("replacements", prompt_builder)
    prompt_and_llm.expose_input("replacements", replacements_passthrough)
    prompt_and_llm.expose_input("model_name", llm)
    prompt_and_llm.expose_input("metadata", metadata_tracker)
    prompt_and_llm.expose_output(llm_response)

    return prompt_and_llm
