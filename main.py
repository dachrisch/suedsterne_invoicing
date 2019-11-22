from google_calendar.service import GoogleCalendarService
from invoicing.billing import MonthlyBillingGenerator


def google_main():
    billing = MonthlyBillingGenerator.with_service(GoogleCalendarService()).generate_billing(2019, 10)

    print(billing)


if __name__ == '__main__':
    google_main()
