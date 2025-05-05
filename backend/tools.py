from utils.tools_utils import tool
import datetime as dt
from datetime import timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from utils.calendar_api_utils import initialize_creds
from typing import List, Union, Optional
import base64
from email.mime.text import MIMEText
import os
from utils.tools_utils import delete_appointment, create_appointment

@tool
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
    output_string = ""

    try:
        service = build("calendar", "v3", credentials=creds)

        now = dt.datetime.now()
        end_time = (now + timedelta(days=days_into_the_future)).isoformat() + "Z"
        now = now.isoformat() + "Z"
        output_string += f"Today's time is: {now}\n"

        event_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            timeMax=end_time,
            maxResults=100,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = event_result.get("items", [])

        if not events:
            if days_into_the_future == 1:
                output_string += "There are no appointments and meetings in the next day."
            else:
                output_string += f"In the next {days_into_the_future} days there are no appointments and meetings."
            return output_string

        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))
            id = event['id']
            output_string += f"Appointment name: {event['summary']}, appointment_id: {id} start: {start}, end: {end}\n"

        return output_string

    except HttpError as error:
        print("An error occurred:", error)
        return "An error occurred while retrieving appointments."

@tool
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

@tool
def create_upcoming_appointment(
    appointment_name: str,
    appointment_description: Optional[str],
    appointment_start_date: str,
    appointment_end_date: str,
    location: Optional[str]
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
    
#@tool
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

        delete_appointment(appointment_ids=appointment_id)

        create_appointment(appointment_name=new_appointment_name, 
                                    appointment_description=new_appointment_description,
                                    appointment_start_date=new_appointment_start_date,
                                    appointment_end_date=new_appointment_end_date,
                                    location=new_location)        

    except HttpError as error:
        print("An error occurred:", error)
        return "An error occurred while creating the appointment."

@tool
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

    out_string = ""

    try:
        query = f'category:primary newer_than:{days_into_the_past}d'
        service = build("gmail", "v1", credentials=creds)
        threads_result = service.users().threads().list(userId='me', q=query).execute()
        threads = threads_result.get('threads', [])

        for thread in threads:
            thread_id = thread['id']
            
            # Get the full thread details
            thread_data = service.users().threads().get(userId='me', id=thread_id).execute()
            
            # Get the first message in the thread
            messages = thread_data.get('messages', [])
            if messages:
                first_message = messages[0]
                
                # Extract headers
                headers = first_message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
                
                out_string += f"Thread ID: {thread_id}, Subject: {subject} \n"

        return out_string

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

# Read mail
@tool
def read_mail(mail_id: str) -> str:
    """
    Retrieves and decodes the plain text content of an email from Gmail using its thread ID.

    Args:
        mail_id (str): The ID of the email thread to read.

    Returns:
        str: The decoded plain text body of the email, or None if an error occurs
        or the body is not found.

    """
    creds = initialize_creds()

    try:
        service = build("gmail", "v1", credentials=creds)
        threads_result = service.users().threads().list(userId='me', q="category:primary").execute()
        threads = threads_result.get('threads', [])

        mail = [thread for thread in threads if thread['id'] == mail_id][0]

        thread_data = service.users().threads().get(userId='me', id=mail_id).execute()
        
        # Get the first message in the thread
        message = thread_data.get('messages', [])[0]
        payload = message.get('payload', {})
        parts = payload.get('parts', [])

        for part in parts:
            if part['mimeType'] == 'text/plain':
                body_data = part['body'].get('data')
                if body_data:
                    decoded_bytes = base64.urlsafe_b64decode(body_data.encode('UTF-8'))
                    return decoded_bytes.decode('UTF-8')

        if payload.get('mimeType') == 'text/plain' and 'data' in payload.get('body', {}):
            body_data = payload['body']['data']
            decoded_bytes = base64.urlsafe_b64decode(body_data.encode('UTF-8'))
            return decoded_bytes.decode('UTF-8')

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

# Send new mail
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
    
def create_morning_breafing():
    """
    This function should say the following things:
        - Any important emails from today?
        - What are the tasks for today?
        - Are there any todos that are for today?
        - Add additional headlines of news what happens today
    """
    pass

if __name__ == "__main__":
    update_upcoming_appointment(appointment_id='aq6euegml32uk49rafk81m9rj0', new_appointment_name="Test 22", new_location="22th street of something")