from utils.agent_utils import Agent
from utils.tools_utils import tool
from tools import get_weather, get_humidity, get_mails, send_mail

@tool
def weather_agent(task_description: str, context: str) -> str:
    """
    Weather agent that processes user weather-related prompts.

    Args:
        task_description (str): A description of the task that this agent needs to complete
        context (str): Additional context provided by previous agents.

    Returns:
        str: A textual response containing the requested weather information.
    """
    weather_agent = Agent(
        name="Weather Agent",
        backstory="You are a weatherman that can always tell what the current temperature is.",
        task_expected_output="Successfull return of what the user wanted",
        task_description=task_description,
        tools=[get_weather, get_humidity]
    )

    weather_agent.receive_context(context)
    output = weather_agent.run(context)
    return output

@tool
def mail_agent(task_description: str, context: str) -> str:
    """
    Mail agent that processes user prompts related to email handling.

    Args:
        task_description (str): A description of the task that this agent needs to complete.
        context (str): Additional context provided by previous agents or surrounding conversation.

    Returns:
        str: A textual response with email details or confirmation of the action taken.
    """
    mail_agent = Agent(
        name="Mail Agent",
        backstory="You are an efficient email assistant who can retrieve or send emails on behalf of the user.",
        task_description=task_description,
        task_expected_output="Successfull return of what the user wanted",
        tools=[get_mails, send_mail]
    )

    mail_agent.receive_context(context)
    output = mail_agent.run(context)
    return output