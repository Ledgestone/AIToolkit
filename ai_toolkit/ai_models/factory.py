# factory.py

from .base import AIModel
from .model_openai import ModelOpenAI
from .model_anthropic import ModelAnthropic
from .model_respell import ModelRespell
from typing import List

class AIModelFactory:
    """
    A factory class for creating instances of AI models.

    This class is designed to create instances of different types of AI models,
    hiding the complexity of the instantiation process from the client code.
    """

    @staticmethod
    def create_model(model_name: str, **kwargs) -> AIModel:
        """
        Create an instance of an AI model.

        This static method creates and returns an instance of an AI model based
        on the provided model name. The model name must match one of the predefined
        names for OpenAI, Anthropic, or Respell models.       

        Args:
            model_name (str): The name of the AI model.
            **kwargs: Arbitrary keyword arguments for model parameters.

        Returns:
            AIModel: An instance of an AI model.

        Raises:
            ValueError: If the model name is not recognized.
        """
        if model_name in ModelOpenAI.MODEL_NAMES:
            return ModelOpenAI(model_name, **kwargs)
        elif model_name in ModelAnthropic.MODEL_NAMES:
            return ModelAnthropic(model_name, **kwargs)
        elif model_name in ModelRespell.MODEL_NAMES:
            return ModelRespell(model_name, **kwargs)
        else:
            raise ValueError(f"Invalid model name: {model_name}")
        
    @staticmethod
    def get_model_names() -> List[str]:
        """
        Get the names of all supported AI models.

        Returns:
            List[str]: A list of all supported AI model names.
        """
        return ModelOpenAI.MODEL_NAMES + ModelAnthropic.MODEL_NAMES + ModelRespell.MODEL_NAMES