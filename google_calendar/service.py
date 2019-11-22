import calendar
from datetime import datetime
from os import path

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class GoogleCalendarService(object):

    def customer_events(self, year: int, month: int, template: str = 'Kunde: '):
        reference = datetime(year=year, month=month, day=1)
        start_of_month = reference.isoformat() + 'Z'
        end_of_month = (reference.replace(
            day=calendar.monthrange(reference.year, reference.month)[1])).isoformat() + 'Z'
        events = self.__calendar_service().events().list(calendarId='primary', timeMin=start_of_month,
                                                         timeMax=end_of_month,
                                                         singleEvents=True,
                                                         orderBy='startTime', q=template).execute().get('items', [])
        return events

    def __calendar_service(self, user_email='cd@it-agile.de'):
        credentials = service_account.Credentials.from_service_account_file(
            path.join(path.join(path.expanduser('~'), '.credentials'), 'suedsterne-1328.json'),
            scopes=SCOPES).with_subject(user_email)

        service = build('calendar', 'v3', credentials=credentials)
        return service
