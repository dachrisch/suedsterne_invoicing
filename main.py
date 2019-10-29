import calendar
from datetime import timedelta

from google.oauth2 import service_account

from google_calendar.service import GoogleCalendarService


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
    customer_billing_sheets = {}
    for calendar_event in GoogleCalendarService().customer_events(2019, 10):
        customer = calendar_event.customer
        if customer not in customer_billing_sheets.keys():
            customer_billing_sheets[customer] = CustomerBillingSheet(customer)

        customer_billing_sheets[customer].add_event(calendar_event)

    for customer_billing_sheet in customer_billing_sheets.values():
        print(customer_billing_sheet.generate_billing())


if __name__ == '__main__':
    google_main()
