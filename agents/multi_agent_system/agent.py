from agents.ToolAgent.tools import Tool
from agents.reActAgent.ReActAgent import ReActAgent
from textwrap import dedent
from agents.multi_agent_system.crew import Crew

class Agent:

    def __init__(
            self,
            name: str, 
            backstory: str, 
            task_description: str, 
            task_expected_output: str,
            model: str = "llama3-70b-8192",
            tools: list[Tool] | None=None,):
        self.name = name
        self.backstory = backstory
        self.task_description = task_description
        self.task_expected_output = task_expected_output
        self.tools = tools
        self.react_agent = ReActAgent(model=model)
        self.dependencies: list[Agent] = []
        self.dependents: list[Agent] = []

        self.context = ""

        Crew.register_agent(self)

    def __repr__(self):
        return f"{self.name}"
    
    def __rshift__(self, other):
        self.add_dependent(other)
        return other
    
    def __lshift__(self, other):
        self.add_dependency(other)
        return other
    
    def __rrshift__(self, other):
        self.add_dependency(other)
        return self
    
    def __rlshift__(self, other):
        self.add_dependent(other)
        return self
    
    def add_dependency(self, other):

        if isinstance(other, Agent):
            self.dependencies.append(other)
            other.dependents.append(self)
        elif isinstance(other, list) and all(isinstance(item, Agent) for item in other):
            for item in other:
                self.dependencies.append(item)
                item.dependents.append(self)
        else:
            raise TypeError("The dependency must be an instance or list of Agent.")
        
    def add_dependent(self, other):

        if isinstance(other, Agent):
            other.dependencies.append(self)
            self.dependents.append(other)
        elif isinstance(other, list) and all(isinstance(item, Agent) for item in other):
            for item in other:
                item.dependencies.append(self)
                self.dependents.append(item)
        else:
            raise TypeError("The dependent must be an instance of the Agent class or a list of Agent instances")
        
    def receive_context(self, input_data):
        self.context += f"{self.name} received the following context: \n{input_data}"

    def create_prompt(self):
        prompt = dedent(
            f"""
        You are an AI agent. You are part of a team of agents working together to complete a task.
        I'm going to give you the task description enclosed in <task_description></task_description> tags. I'll also give
        you the available context from the other agents in <context></context> tags. If the context
        is not available, the <context></context> tags will be empty. You'll also receive the task
        expected output enclosed in <task_expected_output></task_expected_output> tags. With all this information
        you need to create the best possible response, always respecting the format as describe in
        <task_expected_output></task_expected_output> tags. If expected output is not available, just create
        a meaningful response to complete the task.

        <task_description>
        {self.task_description}
        </task_description>

        <task_expected_output>
        {self.task_expected_output}
        </task_expected_output>

        <context>
        {self.context}
        </context>

        Your response:
        """
        ).strip()

        return prompt
    
    def run(self):
        msg = self.create_prompt()
        self.react_agent.bind_tools(self.tools)
        output = self.react_agent.invoke(msg)

        for dependent in self.dependents:
            dependent.receive_context(output)

        return output