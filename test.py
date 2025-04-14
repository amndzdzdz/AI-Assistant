from agents.ToolAgent.ToolAgent import ToolAgent
from agents.ToolAgent.tools import tool

def get_current_wether(city_name: str, country_name: str) -> str:
    """
    This function retrieves the current temperature for a given city.

    Args:
        - city_name (str): The city that you want to know the temperature of
        - country_name (str): The country in which the city is
        
    Return:
        - temperature (str): The temperature in city_name
    """

    temperature = "20 Degrees"

    return temperature

if __name__ == '__main__':
    agent = ToolAgent()
    weather_tool = tool(get_current_wether)
    agent.bind_tools(weather_tool)
    response = agent.invoke("What is the current temperature in Beilngries, Germany?")
    print("response: \n", response)