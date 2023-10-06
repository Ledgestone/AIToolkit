# prompt_and_llm.py

from ..ai_tool import AITool
from ..ai_process import AIProcess
from ai_toolkit.tools import PromptBuilder, AIModel


def PromptAndLLM(name: str) -> AIProcess:
    prompt_builder = PromptBuilder(name)
    ai_model = AIModel(name).set_input(prompt=prompt_builder)

    prompt_and_llm = AIProcess(name)
    prompt_and_llm.expose_input("template", prompt_builder)
    prompt_and_llm.expose_input("replacements", prompt_builder)
    prompt_and_llm.expose_input("model_name", ai_model)
    prompt_and_llm.expose_output(ai_model)

    return prompt_and_llm