from utils.tools_utils import tool

@tool
def get_weather(location: str, unit: str = "celsius") -> dict:
    """
    Retrieves the current temperature for the specified location.

    Args:
        location (str): The location to get the weather for.
        unit (str): The temperature unit ('celsius' or 'fahrenheit').

    Returns:
        dict: A dictionary containing the temperature and unit.
    """
    return {"temperature": 22, "unit": unit}


@tool
def get_humidity(location: str) -> dict:
    """
    Retrieves the current humidity percentage for the specified location.

    Args:
        location (str): The location to get humidity data for.

    Returns:
        dict: A dictionary with the humidity percentage.
    """
    return {"humidity": 65}


@tool
def get_mails(limit: int = 5) -> dict:
    """
    Retrieves recent emails from the user's inbox.

    Args:
        limit (int): The number of emails to retrieve.

    Returns:
        dict: A dictionary containing a list of email summaries.
    """
    emails = [
        {"from": "alice@example.com", "subject": "Meeting Reminder"},
        {"from": "bob@example.com", "subject": "Project Update"},
        {"from": "carol@example.com", "subject": "Invitation"},
    ][:limit]
    return {"emails": emails}


@tool
def send_mail(to: str, subject: str, body: str) -> dict:
    """
    Sends an email with the given subject and body to the specified recipient.

    Args:
        to (str): The recipient's email address.
        subject (str): The subject line of the email.
        body (str): The message body of the email.

    Returns:
        dict: A confirmation message indicating success.
    """
    return {"status": "sent", "to": to, "subject": subject}
