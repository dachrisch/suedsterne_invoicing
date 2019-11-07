import unittest

from app import create_app, InvoiceView
from invoicing.billing import MonthlyBillingServiceGenerator


class TestCalendarService:
    def customer_events(self, year, month):
        return [{'kind': 'calendar#event',
                 'status': 'confirmed',
                 'created': '2019-09-19T15:52:50.000Z',
                 'updated': '2019-10-28T12:24:34.718Z',
                 'summary': 'Kunde: zeppelin',
                 'start': {'date': '2019-10-01'},
                 'end': {'date': '2019-10-02'},
                 'description': 'Action: Coaching\nPrice: 1800 €\nTravel Expense: 100 €'}]


class TestInvoiceApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        InvoiceView.service = MonthlyBillingServiceGenerator(TestCalendarService())

    def test_main_page_produces_month_field(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'type="month"', response.data)

    def test_generate_billing_for_month(self):
        response = self.app.get('/invoice/2019/10', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
