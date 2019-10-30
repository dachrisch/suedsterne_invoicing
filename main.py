import calendar
from datetime import timedelta

from google.oauth2 import service_account

from google_calendar.events import CalendarEvent
from google_calendar.service import GoogleCalendarService
from invoicing.billing import CustomerBilling, MonthlyBilling, MonthlyBillingGenerator


def service_account_main():
    from os import path
    credentials = service_account.Credentials.from_service_account_file(
        path.join(path.join(path.expanduser('~'), '.credentials'), 'suedsterne-1328.json'),
        scopes=SCOPES).with_subject('cd@it-agile.de')
    from googleapiclient.discovery import build
    service = build('calendar', 'v3', credentials=credentials)
    import datetime
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    print(service.events().list(calendarId='primary', timeMin=now,
                                maxResults=10, singleEvents=True,
                                orderBy='startTime').execute())


def google_main():
    billing = MonthlyBillingGenerator.with_service(GoogleCalendarService()).generate_billing(2019, 10)


    print(billing)


if __name__ == '__main__':
    google_main()
