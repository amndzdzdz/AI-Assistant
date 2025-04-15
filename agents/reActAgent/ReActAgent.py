from groq import Groq
from typing import Union, Dict
from ..ToolAgent.tools import tool, Tool, validate_arguments
from ..utils.completion import build_prompt_structure, ChatHistory
from ..utils.extraction import extract_tag_content
from colorama import Fore
import json
import os

BASE_SYSTEM_PROMPT = ""


REACT_SYSTEM_PROMPT = """
You operate by running a loop with the following steps: Thought, Action, Observation.
You are provided with function signatures within <tools></tools> XML tags.
You may call one or more functions to assist with the user query. Don' make assumptions about what values to plug
into functions. Pay special attention to the properties 'types'. You should use those types as in a Python dict.

For each function call return a json object with function name and arguments within <tool_call></tool_call> XML tags as follows:

<tool_call>
{"name": <function-name>,"arguments": <args-dict>, "id": <monotonically-increasing-id>}
</tool_call>

Here are the available tools / actions:

<tools>
%s
</tools>

Example session:

<question>What's the current temperature in Madrid?</question>
<thought>I need to get the current weather in Madrid</thought>
<tool_call>{"name": "get_current_weather","arguments": {"location": "Madrid", "unit": "celsius"}, "id": 0}</tool_call>

You will be called again with this:

<observation>{0: {"temperature": 25, "unit": "celsius"}}</observation>

You then output:

<response>The current temperature in Madrid is 25 degrees Celsius</response>

Additional constraints:

- If the user asks you something unrelated to any of the tools above, answer freely enclosing your answer with <response></response> tags.
"""

class ReActAgent:

    def __init__(self, model: str = "llama3-70b-8192", system_prompt: str = BASE_SYSTEM_PROMPT,):
        self.tools = None
        self.tools_dict = None
        self.model = model
        self.client = Groq(api_key=os.environ.get("groq_api_key"))
        self.system_prompt = system_prompt

    def _model(self, history: list, verbose: int = 0, log_title: str = "COMPLETION", log_color: str = ""):
        chat_completion = self.client.chat.completions.create(
            messages=history,
            model=self.model,
        )

        if verbose > 0:
            print(log_color, f"\n\n{log_title}\n\n", chat_completion)

        return str(chat_completion.choices[0].message.content)

    def bind_tools(self, tools: Union[Tool, list[Tool]]):
        if tools:
            self.tools = tools if isinstance(tools, list) else [tools]
            self.tools_dict = {
                tool.name: tool for tool in self.tools
            }

    def _get_tool_signatures(self):
        return "".join([tool.fn_signature for tool in self.tools])
    
    def process_tool_calls(self, tool_calls_content: list):
        observations = {}

        for tool_call_str in tool_calls_content:
            tool_call = json.loads(tool_call_str)
            tool_name = tool_call["name"]
            tool = self.tools_dict[tool_name]
    
            print(Fore.GREEN + f"\nUsing Tool: {tool_name}")

            validated_tool_call = validate_arguments(tool_call, json.loads(tool.fn_signature))
            print(Fore.GREEN + f"\nTool call dict: \n{validated_tool_call}")

            result = tool.run(**validated_tool_call["arguments"])
            print(Fore.GREEN + f"\nTool result: \n{result}")

            observations[validated_tool_call["id"]] = result
        
        return observations
    
    def invoke(self, message: str, max_iterations: int = 10):
        user_prompt = build_prompt_structure(message, 'user', tag="question")

        if self.tools:
            self.system_prompt += (
                "\n" + REACT_SYSTEM_PROMPT % self._get_tool_signatures()
            )

        chat_history = ChatHistory(
            [
                build_prompt_structure(self.system_prompt, role='system'),
                user_prompt
            ]
        )

        if self.tools:
            
            for _ in range(max_iterations):

                completion = self._model(chat_history)

                response = extract_tag_content(str(completion), "response")

                if response.found:
                    return response.content[0]
                
                thought = extract_tag_content(str(completion), "thought")
                tool_calls = extract_tag_content(str(completion), "tool_call")

                chat_history.append(
                    build_prompt_structure(completion, "assistant")
                )

                print(Fore.MAGENTA + f"\nThought: {thought.content}")

                if tool_calls.found:
                    observations = self.process_tool_calls(tool_calls.content)
                    print(Fore.BLUE + f"\nObservations: {observations}")
                    chat_history.append(
                        build_prompt_structure(f"{observations}", "user")
                    )

        return self._model(chat_history)