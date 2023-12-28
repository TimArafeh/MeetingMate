import os.path
import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar",
          "https://www.googleapis.com/auth/gmail.compose"]

from datetime import datetime
import pytz

from datetime import datetime, timezone
from email.mime.text import MIMEText
import base64

def create_message(sender, to, subject, event):
    start_time = event['start'].get('dateTime', event['start'].get('date'))
    end_time = event['end'].get('dateTime', event['end'].get('date'))

    # Convert UTC to AM/PM format if dateTime is present
    if 'dateTime' in event['start']:
        start_time = convert_utc_to_ampm(start_time)
    if 'dateTime' in event['end']:
        end_time = convert_utc_to_ampm(end_time)

    message_text = f"""
    Hello,

    You have an upcoming one-on-one meeting scheduled in the Accelerator Program.

    Meeting Details:
    Summary: {event['summary']}
    Date & Time: {start_time} to {end_time}
    Location: {event.get('location', 'N/A')}
    Description: {event.get('description', 'No additional description')}

    Please make sure to be present and engage actively in the meeting.

    Best regards,
    [Your Name]
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f"Message Id: {message['id']}")
        return message
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def get_upcoming_events(service, number_of_events=10):
    now = datetime.now(timezone.utc).isoformat()
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=number_of_events, singleEvents=True,
                                          orderBy='startTime').execute()
    return events_result.get('items', [])

def convert_utc_to_ampm(utc_time_str):
    print("Original UTC Time:", utc_time_str)  # Debug print

    # Parse the UTC time string with its timezone offset
    utc_time_with_tz = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%S%z')

    # Convert to local time
    local_time = utc_time_with_tz.astimezone(pytz.timezone('America/Los_Angeles'))
    print("Converted Local Time:", local_time.strftime('%Y-%m-%d %I:%M %p'))  # Debug print

    # Format the time in AM/PM format
    return local_time.strftime('%Y-%m-%d %I:%M %p')


def main():
    creds = None
    exit
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        gmail_service = build("gmail", "v1", credentials=creds)

        upcoming_events = get_upcoming_events(service, number_of_events=10)
        for event in upcoming_events:
            if 'attendees' in event:
                for attendee in event['attendees']:
                    if 'email' in attendee:
                        email = attendee['email']
                        message = create_message('timarafeh2004@gmail.com', email, 'Event Reminder', event)
                        send_message(gmail_service, 'me', message)

        event = {
            "summary": "My Python Event",
            "location": "Somewhere Online",
            "description": "Some more details on this awesome event",
            "colorId": 6,
            "start": {
                "dateTime": "2023-12-28T00:00:00",
                "timeZone": "America/Los_Angeles",

            },

            "end": {
                "dateTime": "2023-12-28T17:00:00",
                "timeZone": "America/Los_Angeles",
                
            },

            "recurrence": [
                "RRULE:FREQ=DAILY;COUNT=1"
            ],

            "attendees": [
                {"email": "timarafeh2004@gmail.com"},
                {"email": "targetemail@mail.com"}
            ]
        }

        event = service.events().insert(calendarId="primary",body=event).execute()
        print(f"Event created {event.get('htmlLink')}")


        for attendee in event['attendees']:
            email = attendee['email']
            message = create_message('timarafeh2004@gmail.com', email, 'Event Reminder', event)
            send_message(gmail_service, 'me', message)



    except HttpError as error:
        print("An error occured: ", error)

if __name__ == "__main__":
    main()