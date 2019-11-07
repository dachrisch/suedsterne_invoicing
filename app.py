import os

from flask import Flask, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_classful import FlaskView, route
from werkzeug.utils import redirect

from google_calendar.service import GoogleCalendarService
from invoicing.billing import MonthlyBillingGenerator, MonthlyBillingServiceGenerator
from web.form import BillingMonthForm


class InvoiceView(FlaskView):
    service: MonthlyBillingServiceGenerator = MonthlyBillingGenerator.with_service(GoogleCalendarService())

    @route('/<year>/<month>')
    def index(self, year, month):
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
    Bootstrap(invoice_app)

    HomeView.register(invoice_app)
    InvoiceView.register(invoice_app)
    return invoice_app


if __name__ == "__main__":
    create_app().run(
        host=os.getenv('INVOICE_SERVICE_HOST', '0.0.0.0'),
        port=os.getenv('INVOICE_SERVICE_PORT', 5000))
