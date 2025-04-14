from typing import Union
from agents.ToolAgent.tools import tool, Tool, validate_arguments
from ..utils.completion import ChatHistory, build_prompt_structure
from ..utils.extraction import extract_tag_content
import os
from groq import Groq
import json 
from colorama import Fore


TOOL_SYSTEM_PROMPT = """
You are a function calling AI model. You are provided with function signatures within <tools></tools> XML tags.
You may call one or more functions to assist with the user query. Don't make assumptions about what values to plug
into functions. Pay special attention to the properties 'types'. You should use those types as in a Python dict.
For each function call return a json object with function name and arguments within <tool_call></tool_call>
XML tags as follows:

<tool_call>
{"name": <function-name>,"arguments": <args-dict>,  "id": <monotonically-increasing-id>}
</tool_call>

Here are the available tools:

<tools>
%s
</tools>
"""

AGENT_SYSTEM_PROMPT = """
You are a tool calling agent that answers questions in a perfect manner.
You are given user question and corresponding tool call observation to answer the questions.
"""

class ToolAgent:
    def __init__(
            self,
            model: str ="llama3-70b-8192"
            ):
        self.tools = None
        self.tools_dict = None
        self.model = model
        self.client = Groq(api_key=os.environ.get("groq_api_key"))

    def _model(self, history: list, verbose: int = 0, log_title: str = "COMPLETION", log_color: str = ""):
        chat_completion = self.client.chat.completions.create(
            messages=history,
            model=self.model,
        )

        if verbose > 0:
            print(log_color, f"\n\n{log_title}\n\n", chat_completion)

        return str(chat_completion.choices[0].message.content)

    def bind_tools(self, tools: Union[Tool, list[Tool]]):
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
    
    def invoke(self, message: str):
        user_prompt = build_prompt_structure(prompt=message, role='user')

        tool_chat_history = ChatHistory(
            [
                build_prompt_structure(
                    prompt=TOOL_SYSTEM_PROMPT % self._get_tool_signatures(),
                    role="system",
                ),
                user_prompt,
            ]
        )

        #agent_chat_history = ChatHistory([user_prompt])
        agent_chat_history = ChatHistory(
            [
                build_prompt_structure(
                    prompt=AGENT_SYSTEM_PROMPT,
                    role="system",
                ),
                user_prompt,
            ]
        )

        tool_call_response = self._model(history=tool_chat_history)

        tool_calls = extract_tag_content(str(tool_call_response), "tool_call")

        if tool_calls.found:
            observations = self.process_tool_calls(tool_calls.content)
            agent_chat_history.append(build_prompt_structure(prompt=f'f"Observation: {observations}"', role="user"))

        return self._model(agent_chat_history)