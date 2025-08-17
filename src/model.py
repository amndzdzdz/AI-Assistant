from typing import Union
from colorama import Fore
import json
import os

from groq import Groq

from utils.tools_utils import validate_arguments, get_fn_signature
from utils.completion_utils import build_prompt_structure, ChatHistory
from utils.extraction_utils import extract_tag_content
from utils.agent_utils import Agent
from utils.tools_utils import Tool


BASE_SYSTEM_PROMPT = ""


REACT_SYSTEM_PROMPT = REACT_SYSTEM_PROMPT = """
You are an agent designed solve complex tasks by utilizing specific tools and your own knowledge.

You operate in a loop with the following steps: Thought → Action (tool call) → Observation.

Your primary responsibilities:
1. Understand the user's query.
2. Plan your approach by breaking down the task into logical steps.
3. Decide which tool to call and in which order.
4. Use the available tool function signatures within <tools></tools> tags to make valid calls.
5. Only use tool calls when absolutely needed; if no tool fits, answer directly.
6. After receiving observations, continue reasoning and potentially plan further actions, or respond with a final answer.

Each function call should return a JSON object within <tool_call></tool_call> tags as follows:

<tool_call>
{"name": <function-name>, "arguments": <args-dict>, "id": <monotonically-increasing-id>}
</tool_call>

Take special care:
- Do not guess values. Only use values grounded in the user query or prior observations.
- Validate that all arguments match the expected 'types' described in the function signatures.
- You may call multiple tools across iterations, but each call must be well-justified in your planning.
- Plan clearly in your <thought> section before taking any <tool_call> action.

Here are the available tools and their capabilities:

<tools>
%s
</tools>

Example interaction:

<question>Can you tell me if the flight LH1234 from Frankfurt to New York is delayed and when it will arrive?</question>

<thought>
To answer this question, I first need to retrieve the flight status of LH1234. I will use the flight tracking agent to get this information.
</thought>

<tool_call>
{"name": "get_flight_status", "arguments": {"flight_number": "LH1234", "date": "today"}, "id": 0}
</tool_call>

<observation>
{0: {"status": "delayed", "delay_reason": "weather"}}
</observation>

<thought>
I now know that the flight is delayed, but the user also asked for the arrival time, which I do not yet have. I need to call the flight ETA agent to retrieve the expected arrival time.
</thought>

<tool_call>
{"name": "get_flight_eta", "arguments": {"flight_number": "LH1234", "date": "today"}, "id": 1}
</tool_call>

<observation>
{1: {"eta": "22:45", "timezone": "EST"}}
</observation>

<response>
The flight LH1234 from Frankfurt to New York is currently delayed due to weather. The estimated time of arrival is 22:45 EST.
</response>

If no tool is suitable for the question, respond freely within <response></response> tags.
Please make sure NOT to include <response></response>-tags when you make an tool_call!!
"""

class Agent:

    def __init__(self, model: str = "llama3-70b-8192", system_prompt: str = BASE_SYSTEM_PROMPT,):
        self.tools = None
        self.tools_dict = None
        self.model = model
        self.client = Groq(api_key=os.environ.get("groq_api_key"))
        self.system_prompt = system_prompt
        self.context = ""

    def _model(self, history: list, verbose: int = 0, log_title: str = "COMPLETION", log_color: str = ""):
        chat_completion = self.client.chat.completions.create(
            messages=history,
            model=self.model,
        )

        if verbose > 0:
            print(log_color, f"\n\n{log_title}\n\n", chat_completion)

        return str(chat_completion.choices[0].message.content)

    def bind_tools(self, tools: Union[str, list[str]]):
        if tools:
            self.tools = tools if isinstance(tools, list) else [tools]
            self.tools_dict = {
                tool.name: tool for tool in self.tools
            }

    def _get_tool_signatures(self) -> str:
        return "".join([get_fn_signature(tool) for tool in self.tools])
    
    def _format_tool(self, tool: str) -> dict:
        formatted_tool = {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": self.tools_dict[tool["name"]].description,
                "parameters": tool["arguments"]
            },
        }
        return formatted_tool
    
    async def process_tool_call(self, tool_calls_content: list, session):
        for tool_call_str in tool_calls_content:
            tool_call = json.loads(tool_call_str)
            tool_call = self._format_tool(tool_call)
            tool_name = tool_call["function"]["name"]

            print(Fore.LIGHTYELLOW_EX + f"\Agent using tool: {tool_name}")

            observation = await session.call_tool(
                tool_call["function"]["name"],
                arguments=tool_call["function"]["parameters"],
            )
            
        return observation.content[0].text
    
    async def invoke(self, message: str, session, max_iterations: int = 10):
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

                print(Fore.MAGENTA + f"\n Agent thought: {thought.content}")

                if tool_calls.found:
                    observations =  await self.process_tool_call(tool_calls.content, session)
                    print(Fore.BLUE + f"\n Agent observations: {observations}")
                    chat_history.append(
                        build_prompt_structure(f"{observations}", "user")
                    )
        return self._model(chat_history)