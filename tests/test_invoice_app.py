import unittest

from app import create_app
from invoicing.billing import MonthlyBillingServiceGenerator
from web.views import InvoiceView


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


class FakeGoogleService(object):
    class JsonWrapper(object):
        def __init__(self, return_json):
            self.return_json = return_json

        def json(self):
            return self.return_json

    def __init__(self, get_options=None):
        self.get_options = get_options

    @property
    def authorized(self):
        return True

    def get(self, url):
        return FakeGoogleService.JsonWrapper(self.get_options[url])


class TestInvoiceApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        InvoiceView.service = MonthlyBillingServiceGenerator(TestCalendarService())
        InvoiceView.auth_service = FakeGoogleService({'/oauth2/v1/userinfo': {'given_name': 'Chris'}})

    def test_main_page_produces_month_field(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'type="month"', response.data)

    def test_generate_billing_for_month(self):
        response = self.app.get('/invoice/2019/10', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
