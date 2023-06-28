# prompt_builder.py

from .prompt_section import PromptSection
from typing import List, Dict, Any

class PromptBuilder:
    """
    A class used to build interactive prompts for conversational AI applications.

    The PromptBuilder class encapsulates system, user, and assistant interactions, 
    providing an easy-to-use interface for constructing dialogues. It also provides 
    functionality to add additional dialogue turns (known as 'shots'). Custom replacement 
    variables can be used within each message, allowing for dynamic message content.

    Methods:
        set_system_prompt: Sets the system's message.
        set_user_prompt: Sets the user's message.
        add_shot: Adds a dialogue turn (a user message and the corresponding assistant's response).
        build: Generates the final list of dialogue turns.

    Usage Example:
    ```python
    builder = PromptBuilder()
    builder.set_system_prompt("Hello, how can I assist you?")
    builder.add_shot("I need help with math.", "Sure, I can help with that.")
    builder.set_user_prompt("What's {{problem}}?")
    replacements = {"problem": "2+2"}  # Add any key-value pairs to be replaced in your prompts here.
    messages = builder.build(replacements)
    ```
    """

    def __init__(self):
        """
        Initializes a new PromptBuilder with empty user and system prompts, 
        and no additional dialog turns (shots).
        """
        self.system_prompt = PromptSection("system")
        self.user_prompt = PromptSection("user").set_prompt("")
        self.shots = []

    def set_system_prompt(self, system_prompt: str) -> None:
        """
        Set the system's message.

        Args:
            system_prompt: The system's message.
        """
        self.system_prompt.set_prompt(system_prompt)

    def set_user_prompt(self, user_prompt: str) -> None:
        """
        Set the user's message.

        Args:
            user_prompt: The user's message.
        """
        self.user_prompt.set_prompt(user_prompt)

    def add_shot(self, user_message: str, assistant_message: str) -> None:
        """
        Add a dialog turn (a shot) to the prompt.

        A shot consists of a user's message and the assistant's response.

        Args:
            user_message: The user's message.
            assistant_message: The assistant's response.
        """
        self.shots.append(PromptSection("user").set_prompt(user_message))
        self.shots.append(PromptSection("assistant").set_prompt(assistant_message))

    def build(self, replacements: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Build the prompt as a list of messages.

        Each message is a dictionary with the keys 'role' (the role of the message sender)
        and 'content' (the message itself). 

        Replacements in the form of "{{key}}" in the message content are replaced by 
        the corresponding values from the replacements dictionary.

        Args:
            replacements: A dictionary of replacements to apply to the message content.

        Returns:
            A list of messages.
        """
        messages = []
        if self.system_prompt.is_set():
            messages.append(self.system_prompt.build_section(replacements))
        for shot in self.shots:
            messages.append(shot.build_section(replacements))
        messages.append(self.user_prompt.build_section(replacements))
        return messages
