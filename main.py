import calendar
from datetime import timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def service_account_main():
    from google.oauth2 import service_account
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


class CustomerCalendarEvent:
    def __init__(self, customer, event_resource):
        from dateutil.parser import parse
        self.customer = customer
        if 'description' in event_resource.keys():
            self.description = event_resource['description']
        else:
            self.description = None

        self.start = parse(event_resource['start'].get('dateTime', event_resource['start'].get('date')))
        self.end = parse(event_resource['end'].get('dateTime', event_resource['end'].get('date')))
        self.status = event_resource['status']

    def duration(self):
        return (self.end - self.start).days

    def __str__(self):
        return "CustomerCalendarEvent(" \
               "customer=%(customer)s, " \
               "description=%(description)s, " \
               "start=%(start)s, end=%(end)s, " \
               "status=%(status)s)" % self.__dict__


def customer_events(year, month, template='Kunde: '):
    import datetime
    service = calendar_service()

    reference = datetime.datetime(year=year, month=month, day=1)
    start_of_month = reference.isoformat() + 'Z'
    end_of_month = (reference.replace(day=calendar.monthrange(reference.year, reference.month)[1])).isoformat() + 'Z'
    return map(lambda event: CustomerCalendarEvent(event['summary'].replace(template, '').lower(), event),
               service.events().list(calendarId='primary', timeMin=start_of_month,
                                     timeMax=end_of_month, singleEvents=True,
                                     orderBy='startTime', q=template).execute().get('items', []))


class CustomerBillingSheet:
    def __init__(self, customer):
        self.customer = customer
        self.events = []
        self.dates=[]

    def add_event(self, event):
        for day in range(0, event.duration()):
            self.dates.append(event.start + timedelta(day))
        self.events.append(event)

    def generate_billing(self):
        return "Kunde: %s, Tage: %s" % (self.customer, self.dates)

    def __str__(self):
        return "CustomerBillingSheet(customer=%(customer)s, events=%(events)s)" % self.__dict__


def google_main():
    customer_billing_sheets = {}
    for calendar_event in customer_events(2019, 10):
        customer = calendar_event.customer
        if customer not in customer_billing_sheets.keys():
            customer_billing_sheets[customer] = CustomerBillingSheet(customer)

        customer_billing_sheets[customer].add_event(calendar_event)

    for customer_billing_sheet in customer_billing_sheets.values():
        print(customer_billing_sheet.generate_billing())


def calendar_service():
    import os
    import pickle
    from os import path
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
    credentials = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
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


if __name__ == '__main__':
    google_main()
