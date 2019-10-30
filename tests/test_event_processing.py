# coding=utf-8

import unittest
from datetime import datetime

from google_calendar.events import CalendarEvent
from invoicing.billing import CustomerBilling, MonthlyBilling


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

        monthly_billing.add(CalendarTestEvent(customer='Konux')).add(
            CalendarTestEvent(customer='Zeppelin'))

        self.assertEqual(len(monthly_billing.customer_billings), 2)
        self.assertIn(CustomerBilling(customer='Konux'), monthly_billing.customer_billings)

    def test_add_multiple_clients_and_activities(self):
        monthly_billing = MonthlyBilling(2019, 10)

        monthly_billing.add(CalendarTestEvent(customer='zeppelin', action='Coaching')).add(
            CalendarTestEvent(customer='konux', action='Scrum Mastering'))

        self.assertEqual(len(monthly_billing.customer_billings), 2)
        self.assertIn(CustomerBilling(customer='konux'), monthly_billing.customer_billings)
        self.assertIn(CustomerBilling(customer='zeppelin'), monthly_billing.customer_billings)


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

        calendar_event = CalendarEvent.from_json(event_json)
        self.assertEqual(calendar_event.customer, 'zeppelin')
        self.assertEqual(calendar_event.date, datetime(2019, 10, 1))
        self.assertEqual(calendar_event.action, 'Coaching')
        self.assertEqual(calendar_event.price, '1800 €')
        self.assertEqual(calendar_event.travel_expenses, '100 €')

    def test_no_description_raises_key_error(self):
        event_json = {'kind': 'calendar#event',
                      'status': 'confirmed',
                      'created': '2019-09-19T15:52:50.000Z',
                      'updated': '2019-10-28T12:24:34.718Z',
                      'summary': 'Kunde: zeppelin',
                      'start': {'date': '2019-10-01'},
                      'end': {'date': '2019-10-02'}}

        with self.assertRaises(KeyError):
            CalendarEvent.from_json(event_json)

    def test_no_travel_expenses_raises_key_error(self):
        event_json = {'kind': 'calendar#event',
                      'status': 'confirmed',
                      'created': '2019-09-19T15:52:50.000Z',
                      'updated': '2019-10-28T12:24:34.718Z',
                      'summary': 'Kunde: zeppelin',
                      'start': {'date': '2019-10-01'},
                      'end': {'date': '2019-10-02'},
                      'description': 'Action: Coaching\nPrice: 1800 €'}

        calendar_event = CalendarEvent.from_json(event_json)
        self.assertEqual(calendar_event.customer, 'zeppelin')
        self.assertEqual(calendar_event.date, datetime(2019, 10, 1))
        self.assertEqual(calendar_event.action, 'Coaching')
        self.assertEqual(calendar_event.price, '1800 €')
        self.assertEqual(calendar_event.travel_expenses, None)

    def test_single_event_to_billing(self):
        event_json = {'kind': 'calendar#event',
                      'status': 'confirmed',
                      'created': '2019-09-19T15:52:50.000Z',
                      'updated': '2019-10-28T12:24:34.718Z',
                      'summary': 'Kunde: zeppelin',
                      'start': {'date': '2019-10-01'},
                      'end': {'date': '2019-10-02'},
                      'description': 'Action: Coaching\nPrice: 1800 €\nTravel Expense: 100 €'}

        calendar_event = CalendarEvent.from_json(event_json)
        self.assertEqual(CustomerBilling.from_event(calendar_event).customer, 'zeppelin')
        self.assertEqual(CustomerBilling.from_event(calendar_event).activities['Coaching'],
                         {'days': [datetime(2019, 10, 1, 0, 0)], 'price': '1800 €'})

    def test_generate_monthly_billing_from_calendar_2_customers(self):
        calendar_event1 = CalendarEvent.from_json({'kind': 'calendar#event',
                                                   'status': 'confirmed',
                                                   'created': '2019-09-19T15:52:50.000Z',
                                                   'updated': '2019-10-28T12:24:34.718Z',
                                                   'summary': 'Kunde: konux',
                                                   'start': {'date': '2019-10-01'},
                                                   'end': {'date': '2019-10-02'},
                                                   'description': 'Action: Coaching\nPrice: 1800 €\nTravel Expense: 100 €'})
        calendar_event2 = CalendarEvent.from_json({'kind': 'calendar#event',
                                                   'status': 'confirmed',
                                                   'created': '2019-09-19T15:52:50.000Z',
                                                   'updated': '2019-10-28T12:24:34.718Z',
                                                   'summary': 'Kunde: zeppelin',
                                                   'start': {'date': '2019-10-01'},
                                                   'end': {'date': '2019-10-02'},
                                                   'description': 'Action: Coaching\nPrice: 1800 €\nTravel Expense: 100 €'})

        billing = MonthlyBilling(2019, 10).add(calendar_event1).add(calendar_event2)

        self.assertEqual(len(billing.customer_billings), 2)
        self.assertIn(CustomerBilling.from_event(calendar_event1), billing.customer_billings)
        self.assertIn(CustomerBilling.from_event(calendar_event2), billing.customer_billings)

    def test_generate_monthly_billing_from_calendar_2_activities(self):
        calendar_event1 = CalendarEvent.from_json({'kind': 'calendar#event',
                                                   'status': 'confirmed',
                                                   'created': '2019-09-19T15:52:50.000Z',
                                                   'updated': '2019-10-28T12:24:34.718Z',
                                                   'summary': 'Kunde: zeppelin',
                                                   'start': {'date': '2019-10-01'},
                                                   'end': {'date': '2019-10-02'},
                                                   'description': 'Action: Coaching\nPrice: 1800 €\nTravel Expense: 100 €'})
        calendar_event2 = CalendarEvent.from_json({'kind': 'calendar#event',
                                                   'status': 'confirmed',
                                                   'created': '2019-09-19T15:52:50.000Z',
                                                   'updated': '2019-10-28T12:24:34.718Z',
                                                   'summary': 'Kunde: zeppelin',
                                                   'start': {'date': '2019-10-03'},
                                                   'end': {'date': '2019-10-02'},
                                                   'description': 'Action: Coaching\nPrice: 1800 €\nTravel Expense: 100 €'})

        billing = MonthlyBilling(2019, 10).add(calendar_event1).add(calendar_event2)

        self.assertEqual(len(billing.customer_billings), 1)
        self.assertIn(CustomerBilling.from_event(calendar_event1), billing.customer_billings)
        self.assertIn(CustomerBilling.from_event(calendar_event2), billing.customer_billings)


class CustomerBillingTest(unittest.TestCase):
    def test_customer_only_to_string(self):
        self.assertEqual(str(CustomerBilling('Konux')), 'CustomerBilling(customer=Konux, activities=[])')

    def test_one_activity_to_string(self):
        self.assertEqual(str(CustomerBilling('Konux').add(CalendarEvent.from_json({'kind': 'calendar#event',
                                                                                   'status': 'confirmed',
                                                                                   'created': '2019-09-19T15:52:50.000Z',
                                                                                   'updated': '2019-10-28T12:24:34.718Z',
                                                                                   'summary': 'Kunde: zeppelin',
                                                                                   'start': {'date': '2019-10-01'},
                                                                                   'end': {'date': '2019-10-02'},
                                                                                   'description':
                                                                                       'Action: Coaching\n'
                                                                                       'Price: 1800 €\n'
                                                                                       'Travel Expense: 100 €'}))),
                         "CustomerBilling(customer=Konux, "
                         "activities=['Coaching: [datetime.datetime(2019, 10, 1, 0, 0)] @ 1800 €', "
                         "'Reisekosten: [datetime.datetime(2019, 10, 1, 0, 0)] @ 100 €'])")
