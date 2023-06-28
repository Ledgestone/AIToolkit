# AIToolkit

AIToolkit is a project that simplifies the creation of interactive prompts for conversational AI models. This repository contains tools to build conversation histories, which can be used to generate context-aware responses in conversational AI applications.

## Getting Started

To use the toolkit, you need to import the necessary modules and adjust your system path to include the location of the AIToolkit directory.

```python
import os
from dotenv import load_dotenv, find_dotenv
from ai_toolkit import AIModelFactory, PromptBuilder
```

## Setup

Before starting, you need to load your environment variables. This project uses a `.env` file to manage environment variables. Make sure to set this up in your project root:

```python
load_dotenv(find_dotenv())
```

Depending on the model that is used, these are the environment variables that will be needed.
- OPENAI_API_KEY
- RESPELL_API_KEY
- ANTHROPIC_API_KEY


## How to Use

### Selecting a Model

To select an AI model, you can use the `AIModelFactory` class. It provides a list of available model names, and you can select one of them to create your AI model:

```python
print(AIModelFactory.get_model_names())
ai_model = AIModelFactory.create_model('selected_model_name')
```

### Building the Prompt

You can construct conversational prompts using the `PromptBuilder` class. This class allows you to set a system message, add dialogue turns (known as 'shots'), and set a user message. You can also use placeholders in your messages that will be replaced with custom values when the prompt is built:

```python
prompt = PromptBuilder()
prompt.set_system_prompt("You are a helpful assistant.")
prompt.add_shot("What is the capital of France?", "Paris")
prompt.add_shot("What is the capital of Netherlands?", "Amsterdam")
prompt.set_user_prompt("What is the capital of {{country}}?")
```

In this example, `{{country}}` is a placeholder that will be replaced with a custom value.

### Getting a Response

After building the prompt, you can use it to get a response from your AI model. The `build` method of `PromptBuilder` takes a dictionary of replacements for the placeholders in your messages:

```python
messages = prompt.build({"country": "Italy"})
ai_model.get_completion(messages)
```

In this example, `{{country}}` is replaced with 'Italy', and the final user message is 'What is the capital of Italy?'. The model is then asked to generate a response based on the constructed conversation history.
