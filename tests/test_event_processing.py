# coding=utf-8

import unittest
from datetime import datetime

from google_calendar.events import CalendarEvent, CalendarEventProcessor


class CustomerBilling(object):
    def __init__(self, customer):
        self.customer = customer
        self.activities = {}

    def add(self, event):
        self.__add_activity(event.action, event.date, event.price)
        if event.travel_expenses:
            self.__add_activity('Reisekosten', event.date, event.travel_expenses)

        return self

    def __add_activity(self, activity, date, price):
        if activity not in self.activities.keys():
            self.activities[activity] = {'days': [], 'price': price}

        self.activities[activity]['days'].append(date)

    def __eq__(self, other):
        if isinstance(other, CustomerBilling):
            return other.customer == self.customer
        return False

    def __hash__(self):
        return hash(self.customer)


class MonthlyBilling(object):
    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.customer_billings = set()

    def add(self, customer_billing):
        self.customer_billings.add(customer_billing)
        return self


class CalendarTestEvent(CalendarEvent):
    def __init__(self, customer='Konux', date=datetime(2019, 10, 21), price=1800, action='Coaching',
                 travel_expense=None):
        CalendarEvent.__init__(self, customer, date, price, action, travel_expense)


class EventProcessingTest(unittest.TestCase):
    def test_creates_billing_from_one_event(self):
        event = CalendarTestEvent()
        billing = CustomerBilling(event.customer)
        self.assertEqual(billing.customer, 'Konux')

    def test_add_activity_to_billing(self):
        billing = CustomerBilling(CalendarTestEvent().customer)

        billing.add(CalendarTestEvent(date=datetime(2019, 10, 7)))
        billing.add(CalendarTestEvent(date=datetime(2019, 10, 21)))
        billing.add(CalendarTestEvent(date=datetime(2019, 10, 23)))

        self.assertEqual([datetime(2019, 10, 7), datetime(2019, 10, 21), datetime(2019, 10, 23)],
                         billing.activities['Coaching']['days'])

    def test_activity_has_price(self):
        billing = CustomerBilling(CalendarTestEvent().customer)

        billing.add(CalendarTestEvent(price=2100))
        self.assertEqual(2100, billing.activities['Coaching']['price'])

    def test_activity_with_travel_expenses(self):
        billing = CustomerBilling(CalendarTestEvent().customer)

        billing.add(CalendarTestEvent(price=2100, action='Coaching', travel_expense=200))
        self.assertEqual(len(billing.activities), 2)
        self.assertEqual(billing.activities['Reisekosten']['price'], 200)


class MonthlyBillingTest(unittest.TestCase):
    def test_add_multiple_clients(self):
        monthly_billing = MonthlyBilling(2019, 10)

        monthly_billing.add(CustomerBilling(customer='Konux')).add(
            CustomerBilling(customer='Zeppelin'))

        self.assertEqual(len(monthly_billing.customer_billings), 2)
        self.assertIn(CustomerBilling(customer='Konux'), monthly_billing.customer_billings)

    def test_add_multiple_clients_and_activities(self):
        monthly_billing = MonthlyBilling(2019, 10)

        monthly_billing.add(CustomerBilling(customer='Konux').add(CalendarTestEvent(action='Coaching'))).add(
            CustomerBilling(customer='Zeppelin').add(CalendarTestEvent(action='Scrum Mastering')))

        self.assertEqual(len(monthly_billing.customer_billings), 2)
        self.assertIn(CustomerBilling(customer='Konux'), monthly_billing.customer_billings)
        self.assertIn(CustomerBilling(customer='Zeppelin'), monthly_billing.customer_billings)


class ProcessCalendarEvents(unittest.TestCase):
    def test_single_day_event_to_object(self):
        event_json = {'kind': 'calendar#event',
                      'status': 'confirmed',
                      'created': '2019-09-19T15:52:50.000Z',
                      'updated': '2019-10-28T12:24:34.718Z',
                      'summary': 'Kunde: zeppelin',
                      'start': {'date': '2019-10-01'},
                      'end': {'date': '2019-10-02'},
                      'description': 'Action: Coaching\nPrice: 1800 €\nTravel Expense: 100 €'}

        calendar_event = CalendarEventProcessor.from_json(event_json)
        self.assertEqual(calendar_event.customer, 'zeppelin')
        self.assertEqual(calendar_event.date, datetime(2019, 10, 1))
        self.assertEqual(calendar_event.action, 'Coaching')
        self.assertEqual(calendar_event.price, '1800 €')
        self.assertEqual(calendar_event.travel_expenses, '100 €')
