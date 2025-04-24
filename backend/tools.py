from utils.tools_utils import tool
import datetime as dt
from datetime import timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from utils.calendar_api_utils import initialize_creds

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
            output_string += f"Appointment name: {event['summary']}, start: {start}, end: {end}\n"

        return output_string

    except HttpError as error:
        print("An error occurred:", error)
        return "An error occurred while retrieving appointments."

if __name__ == "__main__":
    print(get_upcoming_appointments(days_into_the_future=5))