import os

from flask import Flask, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_classful import FlaskView, route
from flask_dance.contrib.google import make_google_blueprint, google
from werkzeug.utils import redirect

from google_calendar.service import GoogleCalendarService
from invoicing.billing import MonthlyBillingGenerator, MonthlyBillingServiceGenerator
from web.form import BillingMonthForm


class InvoiceView(FlaskView):
    service: MonthlyBillingServiceGenerator = MonthlyBillingGenerator.with_service(GoogleCalendarService())
    auth_service = google

    @route('/<year>/<month>')
    def index(self, year, month):
        if not InvoiceView.auth_service.authorized:
            return redirect(url_for('google.login'))

        billing = InvoiceView.service.generate_billing(int(year), int(month))

        return render_template('invoicing.html', billing=billing)


class HomeView(FlaskView):
    route_base = '/'

    def index(self):
        form = BillingMonthForm()
        return render_template('month_chooser.html', form=form)

    def post(self):
        form = BillingMonthForm()
        if form.validate_on_submit():
            return redirect(url_for('InvoiceView:index', year=form.date.data.year, month=form.date.data.month))
        return redirect(url_for('home'))


def create_app():
    invoice_app = Flask(__name__)
    invoice_app.config['SECRET_KEY'] = 'secret'
    blueprint = make_google_blueprint(
        client_id=os.getenv('CLIENT_ID', 'client_id'),
        client_secret=os.getenv('CLIENT_SECRET', 'client_secret'),
    )
    invoice_app.register_blueprint(blueprint, url_prefix="/login")

    Bootstrap(invoice_app)

    HomeView.register(invoice_app)
    InvoiceView.register(invoice_app)
    return invoice_app


if __name__ == "__main__":
    create_app().run(ssl_context='adhoc',
                     host=os.getenv('INVOICE_SERVICE_HOST', 'localhost'),
                     port=os.getenv('INVOICE_SERVICE_PORT', 5000))
