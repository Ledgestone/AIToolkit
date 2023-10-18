# prompt_and_llm.py

from ai_toolkit import AITool
from ai_toolkit.flow import Process
from ai_toolkit.tools import PromptBuilder, LLM


def PromptAndLLM(name: str) -> Process:
    prompt_builder = PromptBuilder(name)
    llm = LLM(name).set_input(prompt=prompt_builder)

    prompt_and_llm = Process(name)
    prompt_and_llm.expose_input("template", prompt_builder)
    prompt_and_llm.expose_input("replacements", prompt_builder)
    prompt_and_llm.expose_input("model_name", llm)
    prompt_and_llm.expose_output(llm)

    return prompt_and_llm
