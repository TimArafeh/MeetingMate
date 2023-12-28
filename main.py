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

import tkinter as tk
from tkinter import messagebox

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


def launch_gui(events, gmail_service):
    root = tk.Tk()
    root.title("MeetingMate")
    root.geometry('1920x1080')
    email_list = ['timarafeh2004@gmail.com', 'speedyslaytaker2004@gmail.com']

    # Frame for emails on the left
    email_frame = tk.Frame(root)
    email_frame.pack(side='left', fill='both', expand=True)

    # Label for email selection
    email_label = tk.Label(email_frame, text="Select email to send reminders to:", font=("Arial", 12))
    email_label.pack(anchor='nw', padx=10, pady=5)

    # Listbox for emails
    email_listbox = tk.Listbox(email_frame, height=20, width=50, selectmode='multiple', exportselection=0,
                               font=("Helvetica", 10), bg="#f7f7f7", fg="#333333",
                               relief='solid', bd=1, highlightthickness=1, highlightbackground="#cccccc")
    email_listbox.pack(side="top", fill="both", expand=True, padx=10, pady=5)

    # Populate the Listbox with email addresses
    for email in email_list:
        email_listbox.insert(tk.END, email)

    # Frame for events on the right
    event_frame = tk.Frame(root)
    event_frame.pack(side='right', fill='both', expand=True)

    # Store checkbox states
    event_checkboxes = {}
    for i, event in enumerate(events):
        # Apply the time conversion for display
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        end_time = event['end'].get('dateTime', event['end'].get('date'))
        if 'dateTime' in event['start']:
            start_time = convert_utc_to_ampm(start_time)
        if 'dateTime' in event['end']:
            end_time = convert_utc_to_ampm(end_time)

        event_description = f"{event['summary']} on {start_time} to {end_time}"
        var = tk.IntVar(value=1)  # Default to checked
        chk = tk.Checkbutton(root, text=event_description, variable=var,
                             font=('Arial',12),
                             activebackground="light blue",
                             bg="light grey",
                             selectcolor="grey",
                             padx=20,
                             pady=5)

        chk.pack(anchor='nw', padx=10, pady=5)
        event_checkboxes[event['id']] = (var, event)

    def on_send_emails():
        selected_indices = email_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "No email selected.")
            return

        for event_id, (var, event) in event_checkboxes.items():
            if var.get() == 1:  # If the checkbox is checked
                for i in selected_indices:
                    selected_email = email_list[i]
                    # Use the selected email to send the message
                    message = create_message('timarafeh2004@gmail.com', selected_email, 'Event Reminder', event)
                    send_message(gmail_service, 'me', message)

        messagebox.showinfo("Info", "Emails sent successfully")
        root.destroy()

    # Send button
    send_btn = tk.Button(root, text="Send Emails", command=on_send_emails)
    send_btn.pack(side='bottom', padx=10, pady=10)

    root.mainloop()

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

        # Launch the GUI for selecting events to send emails
        launch_gui(upcoming_events, gmail_service)

    except HttpError as error:
        print("An error occured: ", error)

if __name__ == "__main__":
    main()