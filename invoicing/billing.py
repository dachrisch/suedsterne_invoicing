import datetime

from google_calendar.events import CalendarEvent


class CustomerBilling(object):
    @staticmethod
    def from_event(event: CalendarEvent):
        return CustomerBilling(event.customer).add(event)

    def __init__(self, customer: str):
        self.customer = customer
        self.activities = {}

    def add(self, event: CalendarEvent):
        self.__add_activity(event.action, event.date, event.price)
        if event.travel_expenses:
            self.__add_activity('Reisekosten', event.date, event.travel_expenses)

        return self

    def __add_activity(self, activity: str, date: datetime, price: str):
        if activity not in self.activities.keys():
            self.activities[activity] = {'days': [], 'price': price}

        self.activities[activity]['days'].append(date)

    def __eq__(self, other):
        if isinstance(other, CustomerBilling):
            return other.customer == self.customer
        return False

    def __hash__(self):
        return hash(self.customer)

    def __str__(self):
        return "CustomerBilling(customer=%s, activities=%s)" % (
            self.customer, ["%s: %s @ %s" % (
                str(activity), self.activities[activity]['days'], self.activities[activity]['price']) for
                            activity in self.activities.keys()])


class MonthlyBilling(object):
    def __init__(self, year: int, month: int):
        self.year = year
        self.month = month
        self.customer_billings = {}

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


class _MonthlyBillingServiceGenerator(object):
    def __init__(self, service):
        self.service = service

    def generate_billing(self, year: int, month: int):
        billing = MonthlyBilling(year, month)
        for calendar_event in self.service.customer_events(year, month):
            billing.add(CalendarEvent.from_json(calendar_event))

        return billing


class MonthlyBillingGenerator(object):
    @staticmethod
    def with_service(service):
        return _MonthlyBillingServiceGenerator(service)
