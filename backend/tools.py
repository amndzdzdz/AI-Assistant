from utils.tools_utils import tool
import datetime as dt
from datetime import timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from utils.calendar_api_utils import initialize_creds
from typing import List, Union, Optional

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

        if isinstance(appointment_ids, str):
            service.events().delete(
                calendarId="primary",
                eventId=appointment_ids,
                sendNotifications=False
            ).execute()
            return "Appointment successfully deleted!"

        elif isinstance(appointment_ids, list):
            for appointment_id in appointment_ids:
                service.events().delete(
                    calendarId="primary",
                    eventId=appointment_id,
                    sendNotifications=False
                ).execute()
            return "Appointments successfully deleted!"

        else:
            return "Invalid input type. Please provide a string or list of strings."

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

        event = {
            'summary': appointment_name,
            'description': appointment_description,
            'location': location,
            'start': {
                'dateTime': appointment_start_date
            },
            'end': {
                'dateTime': appointment_end_date
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Appointment created successfully! View it here: {created_event.get('htmlLink')}"

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

        appointment_name = event['name']
        appointment_start_date = event['start']['dateTime'] + "Z"
        appointment_end_date = event['end']['dateTime'] + "Z"

        if 'description' in event.keys():
            appointment_description = event['description']
        else:
            appointment_description = False

        if 'location' in event.keys():
            location = event['location']
        else:
            location = False

        delete_upcoming_appointments(appointment_id=appointment_id)

        create_upcoming_appointment(app)        


    except HttpError as error:
        print("An error occurred:", error)
        return "An error occurred while creating the appointment."
    


if __name__ == "__main__":
    print(update_upcoming_appointment(appointment_id="6vjpfv0r7rf7cmdj978fjrrc70_20250429T110000Z"))