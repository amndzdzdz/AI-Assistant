from agents.reActAgent.ReActAgent import ReActAgent
from agents.ToolAgent.tools import tool, Tool
from agents.multi_agent_system.crew import Crew
from agents.multi_agent_system.agent import Agent
import math


@tool
def write_str_to_txt(string_data: str, txt_filename: str):
    """
    Writes a string to a txt file.

    This function takes a string and writes it to a text file. If the file already exists, 
    it will be overwritten with the new data.

    Args:
        string_data (str): The string containing the data to be written to the file.
        txt_filename (str): The name of the text file to which the data should be written.
    """
    # Write the string data to the text file
    with open(txt_filename, mode='w', encoding='utf-8') as file:
        file.write(string_data)

    print(f"Data successfully written to {txt_filename}")

if __name__ == '__main__':
    with Crew() as crew:
        agent_1 = Agent(
            name="Poet Agent",
            backstory="You are a well-known poet, who enjoys creating high quality poetry.",
            task_description="Write a poem about the meaning of life",
            task_expected_output="Just output the poem, without any title or introductory sentences",
        )

        agent_2 = Agent(
            name="Poem Translator Agent",
            backstory="You are an expert translator especially skilled in Spanish",
            task_description="Translate a poem into Spanish", 
            task_expected_output="Just output the translated poem and nothing else"
        )

        agent_3 = Agent(
            name="Writer Agent",
            backstory="You are an expert transcriber, that loves writing poems into txt files",
            task_description="You'll receive a Spanish poem in your context. You need to write the poem into './poem.txt' file",
            task_expected_output="A txt file containing the greek poem received from the context",
            tools=[write_str_to_txt],
        )

        agent_1 >> agent_2 >> agent_3

    crew.run()