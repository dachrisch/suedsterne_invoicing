import datetime
from typing import List, Dict

from babel.dates import format_datetime

from google_calendar.events import CalendarEvent


class Price(object):
    def __init__(self):
        self.days: List[datetime.datetime] = []

    @property
    def num_days(self) -> int:
        return len(self.days)

    @property
    def month(self) -> str:
        assert len(set([date.month for date in self.days])) < 2
        return format_datetime(self.days[0], 'MMMM', locale='de')

    @property
    def dates_str(self) -> str:
        return "%s %s" % (', '.join([day.strftime("%-d.") for day in self.days]), self.month)


class Activity(dict):
    def __init__(self):
        super().__init__()
        self.prices: Dict[str, Price] = {}


class CustomerBilling(object):
    @staticmethod
    def from_event(event: CalendarEvent):
        return CustomerBilling(event.customer).add(event)

    def __init__(self, customer: str):
        self.customer = customer
        self.activities: Dict[str, Activity] = {}

    def add(self, event: CalendarEvent):
        self.__add_activity(event.action, event.date, event.price)
        if event.travel_expenses:
            self.__add_activity('Reisekosten', event.date, event.travel_expenses)

        return self

    def __add_activity(self, activity: str, date: datetime, price: str):

        if activity not in self.activities.keys():
            self.activities[activity] = Activity()

        if price not in self.activities[activity].prices.keys():
            self.activities[activity].prices[price] = Price()

        self.activities[activity].prices[price].days.append(date)

    def __eq__(self, other):
        if isinstance(other, CustomerBilling):
            return other.customer == self.customer
        return False

    def __hash__(self):
        return hash(self.customer)


class MonthlyBilling(object):
    def __init__(self, year: int, month: int):
        self.year = year
        self.month = month
        self.customer_billings: Dict[CustomerBilling, CustomerBilling] = {}

    def add(self, event: CalendarEvent):
        customer_billing = CustomerBilling.from_event(event)
        if customer_billing in self.customer_billings:
            self.customer_billings[customer_billing].add(event)
        else:
            self.customer_billings[customer_billing] = customer_billing

        return self

    def __str__(self):
        return "MonthlyBilling(billings=%s)" % ", ".join(
            [str(customer_billing) for customer_billing in self.customer_billings])


class MonthlyBillingServiceGenerator(object):
    def __init__(self, service):
        self.service = service

    def generate_billing(self, year: int, month: int) -> MonthlyBilling:
        billing = MonthlyBilling(year, month)
        for calendar_event in self.service.customer_events(year, month):
            billing.add(CalendarEvent.from_json(calendar_event))

        return billing


class MonthlyBillingGenerator(object):
    @staticmethod
    def with_service(service) -> MonthlyBillingServiceGenerator:
        return MonthlyBillingServiceGenerator(service)
