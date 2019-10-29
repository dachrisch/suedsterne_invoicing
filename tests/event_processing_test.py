import unittest
from datetime import datetime


class CalendarTestEvent(object):
    def __init__(self, customer='Konux', price=1800, date=datetime(2019, 10, 21), action='Coaching',
                 travel_expense=None):
        self.customer = customer
        self.price = price
        self.date = date
        self.action = action
        self.travel_expenses = travel_expense


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

        billing.add(CalendarTestEvent(action='Coaching', price=2100, travel_expense=200))
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
