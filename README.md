# AIToolkit

AIToolkit is a project that simplifies the creation of pipelines utilizing large language models. 

The core concept is the idea of an AITool. Every object in this library is AITool, and AITools can be connected together in just about any way. AITools can be grouped together as an AIProcess, which is also just an AITool.

The main goals are this project is to drive both high flexibility and simplicity. While safeguards can be built into pipelines by users to improve robustness, making these pipelines robust is not the goal of this package (there are many other libraries that aim to do this at the expense of flexibility and/or simplicity). This is why some deliberate design decisions have been made such as:

- **Allowing dynamic inputs to any AITool** - All AITools have certain inputs that are required, but most of them have many optional inputs, and support the user defining their own inputs.
- **Allowing all inputs to be dynamic** - while a lot of LLM libraries (i.e. LangChain, etc.) make you configure certain things in the pipeline such as what LLM model is being used, what templates are used for the prompt, etc. ***Everything*** in the AIToolkit can be dynamically set at runtime through another AITool. So you could have one AIModel decide what model another AIModel uses, or what file a FileReader should read, or even have it write the python code that a Function uses. You could load the template that a PromptBuilder uses from a file, or load the python code that a Function uses from a file. The possibilities are endless!
- **Not enforcing any strict typing on the inputs/outputs** - The user will have to think about how data is being around to ensure type safety as that is not a core feature of this package (it would greatly reduce simplicity)

## Getting Started

The toolkit can be installed using:

`pip install git+https://github.com/Ledgestone/AIToolkit.git`
or
`pdm add git+https://github.com/Ledgestone/AIToolkit.git`

To use the toolkit, you need to import the necessary modules. Here are the typical imports that are probably needed.

```python
from dotenv import load_dotenv, find_dotenv
from ai_toolkit import AIModel, PromptBuilder, FileReader, FileWriter, AIProcess, Function
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

### The core of an AITool

Every AITool has 3 functions that are used. `set_input`, `process`, and `get_output`. Let's look at how you would interact with an LLM using this tool.

```python
llm = AIModel("My LLM")
llm.set_input(model_name="gpt-3.5-turbo", prompt="What is the capital of France?")
llm.process()
print(llm.get_output())
```

This would return something like: `The capital of France is Paris`. 

Note that all methods are chainable so this would be equivalent to:
```python
prompt = "What is the capital of France?"
print(AIModel("My LLM").set_input(model_name="gpt-3.5-turbo", prompt=prompt).process().get_output())
```

### Using multiple AITools together

The above example isn't very interesting, since only one AITool is in use. Let's now look at adding in a `PromptBuilder`

```python
prompt = PromptBuilder("My Prompt").set_input(template="What is the capital of {{country}}", country="France")
llm = AIModel("My LLM").set_input(model_name="gpt-3.5-turbo", prompt=prompt)

prompt.process()
llm.process()
print(llm.get_output())
```

As you can see from this example, it is easy to chain together different AITools. Any input can be another AITool, and as long as all inputs have processed, the current AITool will be able to process as well.

### Using an AIProcess

It can become tedious to process several AITools that have been chained together, so AITools can be grouped together using an AIProcess, so that they can all be processed at once as another AITool.

Let's first define several AITools that we want to group into a process:

```python
dishes_file = FileReader("Possible Dishes File Reader").set_input(file_path="possible_dishes_prompt.txt")
dishes_prompt = PromptBuilder("Possible Dishes Prompt").set_input(template=dishes_file)
dishes_llm = AIModel("Possible Dishes LLM").set_input(model_name="gpt-3.5-turbo", prompt=dishes_prompt)
dishes_json = Function("Possible Dishes JSON").set_input(function="convert_to_json", input=dishes_llm)
dishes_file_writer = FileWriter("Possible Dishes File Writer").set_input(file_path="possible_dishes.json", data=dishes_json)
```

After defining these AITools, let's create our AIProcess:

```python
dish_generator = AIProcess("Possible Dishes Process")
dish_generator.expose_input("ingredients", dishes_prompt)
dish_generator.expose_output(dishes_json)
```

Now we have a dish_generator that has the input `ingredients`, and outputs 3 dishes that it generates as an array. It also saves these dishes to a json file to be able to go back to. The AIProcess automatically determines all AITools in the process by analyzing the links between the AITools defined in the inputs and outputs.

Now we can use the `dish_generator` just like any other AITool:
```python
dish_generator.set_input(ingredients="chicken, rice, and broccoli")
dish_generator.process()
print(dish_generator.get_output())
```

Note again that the input here for `ingedients` could also be another AITool.

## Roadmap (Right now just a list of goals)
- Create a loop tool that wraps around another tool and performs some operation multiple times over that tool
    - Allow the loop tool to specify a certain number of threads to allow parallelization
- Create a retry tool that checks a certain condition and if that condition is not satisfied it will try running the tool again
- Implement automated retries for common errors with LLMs, with support for a timout period
- Add a `.debug()` function to AITool that will nicely log the inputs and outputs of any AITool, with the option to specify a file to save these logs to.
- Add better documentation so that on hover it is easy to see what the inputs are for any given AITool, along with examples of valid inputs (especially for AIModel & Function)
- Create an example of how you would set up an AIProcess that automatically adjusts which LLM Model is used depending on the number of tokens in the prompt.
- Create an AITool for interacting with a key/value store database
- Create an AITool for creating and retrieving embeddings
- Add the abililty to pass in Callables to the function, so it doesn't require executing code from a string
