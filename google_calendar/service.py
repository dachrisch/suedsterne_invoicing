import calendar
import pickle
from datetime import datetime
from os import path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class GoogleCalendarService(object):
    def __init__(self):
        self.service = self.__calendar_service()

    def customer_events(self, year, month, template='Kunde: '):

        reference = datetime(year=year, month=month, day=1)
        start_of_month = reference.isoformat() + 'Z'
        end_of_month = (reference.replace(
            day=calendar.monthrange(reference.year, reference.month)[1])).isoformat() + 'Z'
        events = self.service.events().list(calendarId='primary', timeMin=start_of_month, timeMax=end_of_month,
                                            singleEvents=True,
                                            orderBy='startTime', q=template).execute().get('items', [])
        return events

    def __calendar_service(self):
        """Shows basic usage of the Google Calendar API.
            Prints the start and name of the next 10 events on the user's calendar.
            """
        credentials = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                credentials = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    path.join(path.join(path.expanduser('~'), '.credentials'), 'cal.json'), SCOPES)
                credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(credentials, token)
        service = build('calendar', 'v3', credentials=credentials)
        return service
