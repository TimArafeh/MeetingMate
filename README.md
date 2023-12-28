# MeetingMate

NOTE: This program depends on a token.json file and a credentials.json file, to properly use this program you will need to authenticate your own tokens for the APIs to work properly, I removed the already existing token and credential files as they pose to be a security risk.

This Python script is designed to integrate with the Google Calendar and Gmail APIs to automate the process of sending reminders for upcoming events. It features a user interface built with Tkinter, which allows users to select one-on-one meetings from their Google Calendar and send email reminders to the participants.

Key Features:

- Google API Integration: Utilizes the Google Calendar API to fetch upcoming events and the Gmail API to compose and send emails.
- Authentication Handling: Manages OAuth2 authentication, storing credentials securely for easy access without constant reauthentication.
- Email Composition: Generates email messages in MIME format, including event details such as summary, date, time, location, and description.
- Event Retrieval: Obtains a list of the next ten upcoming events from the user's primary Google Calendar.
- Timezone Conversion: Converts event times from UTC to Pacific Time (PT) in a human-readable AM/PM format.
- Graphical User Interface (GUI): Provides a two-panel layout with a list box for selecting email addresses on the left and checkboxes for upcoming events on the right.
- Batch Email Sending: Allows the user to select multiple events and send reminders to multiple email addresses in one operation.
- Error Handling: Catches and prints out any HTTP errors that occur during API calls.

How It Works:

Authentication: On startup, the script checks for existing Google API credentials. If none are found or if they have expired, it initiates a login flow to authenticate the user and obtain the necessary tokens.

Upcoming Events Fetching: Once authenticated, the script requests the upcoming events from the user's Google Calendar, filtering for one-on-one meetings.

GUI Presentation: The script launches a Tkinter-based GUI, displaying a list of emails on the left side and a list of upcoming events on the right side. Users can select which emails to send reminders to and which events they pertain to.

Email Reminder Composition: For each selected event, the script creates an email reminder with details of the event, formatted in a friendly message template.

Email Sending: After the user confirms their selection, the script sends out the email reminders to the chosen recipients, using the Gmail API.

Session End: Upon successful sending of reminders, the script informs the user and closes the GUI.

Usage:

This script is intended for program managers or individuals who need to manage event reminders efficiently. It requires a client secret file from Google API Console with appropriate permissions for the Google Calendar and Gmail APIs.
