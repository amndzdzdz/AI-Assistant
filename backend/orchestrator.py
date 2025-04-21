from groq import Groq
from typing import Union, Dict
from utils.tools_utils import tool, Tool, validate_arguments
from utils.completion import build_prompt_structure, ChatHistory
from utils.extraction import extract_tag_content
from agents import weather_agent, mail_agent
from utils.agent_utils import Agent
from colorama import Fore
import json
import os

BASE_SYSTEM_PROMPT = ""


REACT_SYSTEM_PROMPT = REACT_SYSTEM_PROMPT = """
You are the orchestrator of a multi-agent system designed to solve complex tasks by delegating work to specialized agents.

You operate in a loop with the following steps: Thought → Action (agent call) → Observation.

Your primary responsibilities:
1. Understand the user's query.
2. Plan your approach by breaking down the task into logical steps.
3. Decide which agents to call and in which order.
4. Use the available agent function signatures within <agents></agents> tags to make valid calls.
5. Only use agent calls when absolutely needed; if no agent fits, answer directly.
6. After receiving observations, continue reasoning and potentially plan further actions, or respond with a final answer.

Each function call should return a JSON object within <agent_call></agent_call> tags as follows:

<agent_call>
{"name": <function-name>, "arguments": <args-dict>, "id": <monotonically-increasing-id>}
</agent_call>

Take special care:
- Do not guess values. Only use values grounded in the user query or prior observations.
- Validate that all arguments match the expected 'types' described in the function signatures.
- You may call multiple agents across iterations, but each call must be well-justified in your planning.
- Plan clearly in your <thought> section before taking any <agent_call> action.

Here are the available agents and their capabilities:

<agents>
%s
</agents>

Example interaction:

<question>Can you tell me if the flight LH1234 from Frankfurt to New York is delayed and when it will arrive?</question>

<thought>
To answer this question, I first need to retrieve the flight status of LH1234. I will use the flight tracking agent to get this information.
</thought>

<agent_call>
{"name": "get_flight_status", "arguments": {"flight_number": "LH1234", "date": "today"}, "id": 0}
</agent_call>

<observation>
{0: {"status": "delayed", "delay_reason": "weather"}}
</observation>

<thought>
I now know that the flight is delayed, but the user also asked for the arrival time, which I do not yet have. I need to call the flight ETA agent to retrieve the expected arrival time.
</thought>

<agent_call>
{"name": "get_flight_eta", "arguments": {"flight_number": "LH1234", "date": "today"}, "id": 1}
</agent_call>

<observation>
{1: {"eta": "22:45", "timezone": "EST"}}
</observation>

<response>
The flight LH1234 from Frankfurt to New York is currently delayed due to weather. The estimated time of arrival is 22:45 EST.
</response>


If no agent is suitable for the question, respond freely within <response></response> tags.
"""

class Orchestrator:

    def __init__(self, model: str = "llama3-70b-8192", system_prompt: str = BASE_SYSTEM_PROMPT,):
        self.agents = None
        self.agents_dict = None
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

    def bind_agents(self, agents: Union[Agent, list[Agent]]):
        if agents:
            self.agents = agents if isinstance(agents, list) else [agents]
            self.agents_dict = {
                agent.name: agent for agent in self.agents
            }

    def _get_agent_signatures(self):
        return "".join([agent.fn_signature for agent in self.agents])
    
    def process_agent_call(self, agent_calls_content: list):
        observations = {}

        for agent_call_str in agent_calls_content:
            agent_call = json.loads(agent_call_str)
            agent_name = agent_call["name"]
            agent = self.agents_dict[agent_name]
    
            print(Fore.LIGHTYELLOW_EX + f"\nOrchestrator using agent: {agent_name}")

            validated_agent_call = validate_arguments(agent_call, json.loads(agent.fn_signature))
            print(Fore.LIGHTYELLOW_EX + f"\n Orchestrator agent call dict: \n{validated_agent_call}")

            result = agent.run(**validated_agent_call["arguments"])
            print(Fore.LIGHTYELLOW_EX + f"\nagent result: \n{result}")

            observations[validated_agent_call["id"]] = result
        
        return observations
    
    def invoke(self, message: str, max_iterations: int = 10):
        user_prompt = build_prompt_structure(message, 'user', tag="question")

        if self.agents:
            self.system_prompt += (
                "\n" + REACT_SYSTEM_PROMPT % self._get_agent_signatures()
            )

        chat_history = ChatHistory(
            [
                build_prompt_structure(self.system_prompt, role='system'),
                user_prompt
            ]
        )

        if self.agents:
            
            for _ in range(max_iterations):

                completion = self._model(chat_history)

                response = extract_tag_content(str(completion), "response")

                if response.found:
                    return response.content[0]
                
                thought = extract_tag_content(str(completion), "thought")
                agent_calls = extract_tag_content(str(completion), "agent_call")

                chat_history.append(
                    build_prompt_structure(completion, "assistant")
                )

                print(Fore.MAGENTA + f"\n Orchestrator thought: {thought.content}")

                if agent_calls.found:
                    observations = self.process_agent_call(agent_calls.content)
                    print(Fore.BLUE + f"\n Orchestrator observations: {observations}")
                    chat_history.append(
                        build_prompt_structure(f"{observations}", "user")
                    )

        return self._model(chat_history)
    
if __name__ == '__main__':
    orchestrator = Orchestrator()
    orchestrator.bind_agents([weather_agent, mail_agent])
    response = orchestrator.invoke("Can you display my mails?")
    print(response)