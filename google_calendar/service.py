import calendar
from datetime import datetime
from os import path

from googleapiclient.discovery import build
from googleapiclient.http import build_http

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

    def __calendar_service(self):
        from oauth2client import client, file, tools
        client_secret = path.join(path.join(path.expanduser('~'), '.credentials', 'calendar.json'))
        storage = file.Storage('.cal_store')
        credentials = storage.get()
        flow = client.flow_from_clientsecrets(client_secret, scope=SCOPES,
                                              message=tools.message_if_missing(client_secret))
        if credentials is None or credentials.invalid:
            credentials = tools.run_flow(flow, storage)
        http = credentials.authorize(http=build_http())
        service = build('calendar', 'v3', http=http)
        storage.delete()
        return service
