from utils.tools_utils import tool
import datetime as dt
from datetime import timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from utils.calendar_api_utils import initialize_creds
from typing import List, Union

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
            output_string += f"Appointment name: {event['summary']}, appointmentId: {id} start: {start}, end: {end}\n"

        return output_string

    except HttpError as error:
        print("An error occurred:", error)
        return "An error occurred while retrieving appointments."

@tool
def delete_upcoming_appointments(appointmentIds: Union[str, List[str]]) -> str:
    """
    Deletes one or multiple upcoming Google Calendar appointments by their appointment ID(s).

    Parameters:
        appointmentIds (Union[str, List[str]]): A single appointment ID as a string, or a list of 
                                                appointment IDs to delete.

    Returns:
        str: A message indicating whether the deletion was successful or if an error occurred.
    """

    creds = initialize_creds()

    try:
        service = build("calendar", "v3", credentials=creds)

        if isinstance(appointmentIds, str):
            service.events().delete(
                calendarId="primary",
                eventId=appointmentIds,
                sendNotifications=False
            ).execute()
            return "Appointment successfully deleted!"

        elif isinstance(appointmentIds, list):
            for appointmentId in appointmentIds:
                service.events().delete(
                    calendarId="primary",
                    eventId=appointmentId,
                    sendNotifications=False
                ).execute()
            return "Appointments successfully deleted!"

        else:
            return "Invalid input type. Please provide a string or list of strings."

    except HttpError as error:
        print("An error occurred:", error)
        return "An error occurred while deleting appointments."

if __name__ == "__main__":
    print(delete_upcoming_appointments(appointmentIds=['fvqqturou0u4pg12ceshc4tjss', '9rnqiuk5iofo5v068i8a3j50c8']))