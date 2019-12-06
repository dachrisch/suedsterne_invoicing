from flask import url_for, render_template
from flask_classful import FlaskView, route
from flask_dance.contrib.google import google
from oauthlib.oauth2 import TokenExpiredError
from werkzeug.utils import redirect

from google_calendar.service import GoogleCalendarService
from invoicing.billing import MonthlyBillingServiceGenerator, MonthlyBillingGenerator
from web.form import BillingMonthForm


class InvoiceView(FlaskView):
    service: MonthlyBillingServiceGenerator = MonthlyBillingGenerator.with_service(GoogleCalendarService())
    auth_service = google

    @route('/<year>/<month>')
    def index(self, year, month):
        if not InvoiceView.auth_service.authorized:
            return redirect(url_for('google.login'))

        try:
            billing = InvoiceView.service.generate_billing(int(year), int(month))
            return render_template('invoicing.html', billing=billing,
                                   name=GoogleUserInfo(InvoiceView.auth_service).mate)
        except TokenExpiredError:
            return redirect(url_for('google.login'))


class HomeView(FlaskView):
    route_base = '/'
    auth_service = google

    def index(self):
        if not HomeView.auth_service.authorized:
            return redirect(url_for('google.login'))
        try:
            form = BillingMonthForm()
            return render_template('month_chooser.html', form=form, name=GoogleUserInfo(HomeView.auth_service).mate)
        except TokenExpiredError:
            return redirect(url_for('google.login'))

    def post(self):
        form = BillingMonthForm()
        if form.validate_on_submit():
            return redirect(url_for('InvoiceView:index', year=form.date.data.year, month=form.date.data.month))
        return redirect(url_for('home'))


class GoogleUserInfo(object):
    def __init__(self, google_service):
        self.google_service = google_service

    @property
    def mate(self):
        return self._user_info()['given_name']

    def _user_info(self):
        return self.google_service.get("/oauth2/v1/userinfo").json()
