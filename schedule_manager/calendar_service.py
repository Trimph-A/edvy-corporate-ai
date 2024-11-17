from typing import List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from .utils import load_config
import yaml
import datetime
import os

config = load_config('config/config.yaml')

SERVICE_ACCOUNT_FILE = config['google']['service_account_file']
SCOPES = config['google']['scopes']

# Load credentials from the service account file
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Build the Google Calendar API service
calendar_service = build('calendar', 'v3', credentials=credentials)

def check_availability(calendar_id: str, start_time: datetime.datetime, end_time: datetime.datetime) -> bool:
    """
    Checks if a user is available for the given time range.
    """
    events = calendar_service.events().list(
        calendarId=calendar_id,
        timeMin=start_time.isoformat() + 'Z',
        timeMax=end_time.isoformat() + 'Z',
        singleEvents=True
    ).execute()

    return not events.get('items', [])

def schedule_meeting_event(calendar_ids: list, start_time: datetime.datetime, end_time: datetime.datetime) -> dict:
    """
    Schedules a meeting with one or more users.
    """
    event = {
        'summary': 'Proposed Meeting',
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'},
        'attendees': [{'email': calendar_id} for calendar_id in calendar_ids],
        'conferenceData': {
            'createRequest': {
                'requestId': 'random-string',
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
            }
        }
    }

    created_event = calendar_service.events().insert(
        calendarId=calendar_ids[0], 
        body=event,
        conferenceDataVersion=1
    ).execute()

    return created_event

def check_group_availability(group_members: List[str], start_time: datetime.datetime, end_time: datetime.datetime) -> bool:
    """
    Checks if all members of a group are available for the given time range.
    """
    for calendar_id in group_members:
        if not check_availability(calendar_id, start_time, end_time):
            return False
    return True
