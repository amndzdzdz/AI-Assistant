import os
import base64
import email
from dotenv import load_dotenv
from typing import List, Union, Optional

from googleapiclient.discovery import build
from dataclasses import dataclass
from fastmcp import FastMCP
from textwrap import dedent
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText

from src.utils.completion_utils import call_groq_api
from utils.google_api_utils import initialize_creds
from src.utils.tools_utils import (
    delete_appointment, 
    create_appointment, 
    get_appointments, 
    get_emails, scrape_news
)

load_dotenv()

mcp = FastMCP(
    name="agent_assistanc"
)

@mcp.tool
def get_upcoming_appointments(days_into_the_future: int) -> str:
    """
    Fetches and formats upcoming Google Calendar appointments within a specified time range.

    Parameters:
        days_into_the_future (int): The number of days into the future to look for upcoming appointments.

    Returns:
        str: A formatted string listing all appointments within the given range, or a message
             indicating that no appointments are scheduled.
    """
    creds = initialize_creds()

    try:
        service = build("calendar", "v3", credentials=creds)
        result = get_appointments(days_into_the_future, service)
        return result
    except HttpError as error:
        print("An error occurred:", error)
        return "An error occurred while retrieving appointments."

@mcp.tool
def delete_upcoming_appointments(appointment_ids: Union[str, List[str]]) -> str:
    """
    Deletes one or multiple upcoming Google Calendar appointments by their appointment ID(s).

    Parameters:
        appointment_ids (Union[str, List[str]]): A single appointment ID as a string, or a list of 
                                                appointment IDs to delete.

    Returns:
        str: A message indicating whether the deletion was successful or if an error occurred.
    """
    creds = initialize_creds()

    try:
        service = build("calendar", "v3", credentials=creds)
        result = delete_appointment(appointment_ids= appointment_ids, service=service)
        return result
    except HttpError as error:
        print("An error occurred:", error)
        return "An error occurred while deleting appointments."

@mcp.tool
def create_upcoming_appointment(
    appointment_name: str,
    appointment_start_date: str,
    appointment_end_date: str,
    appointment_description: Optional[str] = "",
    location: Optional[str] = ""
) -> str:
    """
    Creates a new appointment in the user's Google Calendar.

    Parameters:
        appointment_name (str): The title or summary of the appointment.
        appointment_description (Optional[str]): An optional description of the appointment. Place an empty string if no further information is provided.
        appointment_start_date (str): The start datetime in ISO 8601 format (e.g., '2025-04-24T14:00:00+02:00').
        appointment_end_date (str): The end datetime in ISO 8601 format (e.g., '2025-04-24T16:00:00+02:00').
        location (Optional[str]): An optional location for the appointment. Place an empty string if no further information is provided.

    Returns:
        str: A message confirming the appointment creation or reporting an error.
    """
    creds = initialize_creds()

    try:
        service = build("calendar", "v3", credentials=creds)
        result = create_appointment(appointment_name=appointment_name,
                                    appointment_description=appointment_description,
                                    appointment_start_date=appointment_start_date,
                                    appointment_end_date=appointment_end_date,
                                    location=location,
                                    service=service)
        return result
    except HttpError as error:
        print("An error occurred:", error)
        return "An error occurred while creating the appointment."

@mcp.tool
def update_upcoming_appointment(
    appointment_id: str,
    new_appointment_name: Optional[str] = "",
    new_appointment_description: Optional[str] = "",
    new_appointment_start_date: Optional[str] = "",
    new_appointment_end_date: Optional[str] = "",
    new_location: Optional[str] = ""
) -> str:
    """
    Creates a new appointment in the user's Google Calendar.

    Parameters:
        appointment_name (str): The title or summary of the appointment.
        appointment_description (Optional[str]): An optional description of the appointment. Place an empty string if no further information is provided.
        appointment_start_date (str): The start datetime in ISO 8601 format (e.g., '2025-04-24T14:00:00+02:00').
        appointment_end_date (str): The end datetime in ISO 8601 format (e.g., '2025-04-24T16:00:00+02:00').
        location (Optional[str]): An optional location for the appointment. Place an empty string if no further information is provided.

    Returns:
        str: A message confirming the appointment creation or reporting an error.
    """
    creds = initialize_creds()

    try:
        service = build("calendar", "v3", credentials=creds)
        event = service.events().get(calendarId="primary", eventId=appointment_id).execute()

        appointment_name = event['summary']
        appointment_start_date = event['start']['dateTime']
        appointment_end_date = event['end']['dateTime']

        if 'description' in event.keys():
            appointment_description = event['description']
        else:
            appointment_description = ""

        if 'location' in event.keys():
            location = event['location']
        else:
            location = ""

        if len(new_appointment_name) == 0:
            new_appointment_name = appointment_name

        if len(new_appointment_description) == 0:
            new_appointment_description = appointment_description

        if len(new_appointment_start_date) == 0:
            new_appointment_start_date = appointment_start_date

        if len(new_appointment_end_date) == 0:
            new_appointment_end_date = appointment_end_date

        if len(new_location) == 0:
            new_location = location

        create_appointment(
            new_appointment_name, 
            new_appointment_description,
            new_appointment_start_date,
            new_appointment_end_date,
            new_location,
            service
        )    
        delete_appointment(appointment_ids=appointment_id, service=service)    
    except HttpError as error:
        print("An error occurred:", error)
        return "An error occurred while creating the appointment."

@mcp.tool
def display_recent_emails(days_into_the_past: int) -> str:
    """
    Displays the subject lines and thread IDs of recent emails in the Gmail account
    based on the number of days provided.

    Args:
        days_into_the_past (int): The number of days in the past to search for emails.
    
    Returns:
        str: A string containing thread IDs and subjects of the emails. Returns None if no emails are found or an error occurs.
    """
    creds = initialize_creds()

    try:
        service = build("gmail", "v1", credentials=creds)
        result = get_emails(days_into_the_past, service)
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return f"An error occured when fetching emails of the last {days_into_the_past} days"

@mcp.tool
def read_mail(thread_id: str) -> str:
    """
    Retrieves and decodes the plain text content of an email from Gmail using its thread ID.

    Args:
        thread_id (str): The ID of the email thread to read.

    Returns:
        str: The decoded plain text body of the email, or None if an error occurs
        or the body is not found.

    """
    creds = initialize_creds()

    try:
        service = build("gmail", "v1", credentials=creds)
        email_message = service.users().messages().get(userId='me', id=thread_id, format='raw').execute()

        msg_str = base64.urlsafe_b64decode(email_message['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(msg_str)
        
        def get_mime_body(mime_msg):
            if mime_msg.is_multipart():
                for part in mime_msg.walk():
                    ctype = part.get_content_type()
                    dispo = str(part.get('Content-Disposition') or '')
                    if "attachment" in dispo:
                        continue
                    if ctype == 'text/plain':
                        return part.get_payload(decode=True).decode(errors="replace")
                for part in mime_msg.walk():
                    if part.get_content_type() == 'text/html':
                        return part.get_payload(decode=True).decode(errors="replace")
            else:
                return mime_msg.get_payload(decode=True).decode(errors="replace")
            return None
        
        decoded_msg = get_mime_body(mime_msg)
        return decoded_msg
    except HttpError as error:
        print(f"An error occurred: {error}")
        return f"An error occured when reading an email."

@mcp.tool
def send_mail(message_text: str, to: str, subject: str) -> str:
    """
    Sends an email using the Gmail API.

    Args:
        message_text (str): The plain text content of the email message.
        to (str): The recipient's email address.
        subject (str): The subject line of the email.

    Returns:
        str: A response whether or not the tool call was successfull
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = os.getenv("sender_mail")
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}
    creds = initialize_creds()

    try:
        service = build("gmail", "v1", credentials=creds)
        message = service.users().messages().send(userId="me", body=body).execute()
        return "The email was successfully sent!"
    except HttpError as error:
        print('An error occurred: %s' % error)
        return None

@mcp.tool
def create_morning_briefing() -> str:
    """
    Generates a morning briefing containing:
    - Recent important emails (from the past 3 days)
    - Today's appointments and to-dos
    - Headlines from today's news

    Returns:
        A formatted string with the summarized information.
    """
    creds = initialize_creds()

    try:
        mail_service = build("gmail", "v1", credentials=creds)
        calendar_service = build("calendar", "v3", credentials=creds)
        past_emails = get_emails(days_into_the_past=3, service=mail_service)
        future_appointments = get_appointments(days_into_the_future=1, service=calendar_service)
        #The news_headlines should be added to the prompt, 
        #but I cant access more tokens due to my free grok tier.
        #news_headlines = scrape_news()

        prompt = dedent(f"""
        Past Emails:
        {past_emails}

        Future Appointments:
        {future_appointments}
        """).strip()

        message = {'role': 'user', 'content': f'Create a morning briefing using the following information: {prompt}'}
        morning_briefing = call_groq_api(message)
        return morning_briefing
    except Exception as e:
        return f"Failed to generate morning briefing: {str(e)}"
    except:
        print("An error occured!")

if __name__ == '__main__':
    mcp.run(transport="sse", host="127.0.0.1", port=8000)