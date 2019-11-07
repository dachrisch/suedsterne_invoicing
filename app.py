import os

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from wtforms.widgets import Input
from wtforms.widgets.html5 import DateInput

from google_calendar.service import GoogleCalendarService
from invoicing.billing import MonthlyBillingGenerator

invoice_app = Flask(__name__)
invoice_app.config['SECRET_KEY'] = 'secret'
Bootstrap(invoice_app)


class MonthInput(Input):
    input_type = 'month'


class MonthField(DateField):
    widget = MonthInput()


class BillingMonthForm(FlaskForm):
    date = MonthField(u'Billing Month', validators=[DataRequired('please state month')], format="%Y-%m")
    submit = SubmitField('Submit')


@invoice_app.route("/", methods=['GET', 'POST'])
def home():
    form = BillingMonthForm()
    if form.validate_on_submit():
        date = form.date.data
        billing = MonthlyBillingGenerator.with_service(GoogleCalendarService()).generate_billing(date.year, date.month)

        return render_template('invoicing.html', billing=billing)

    return render_template('month_chooser.html', form=form)


if __name__ == "__main__":
    invoice_app.run(host=os.getenv('INVOICE_SERVICE_HOST', '0.0.0.0'),
                    port=os.getenv('INVOICE_SERVICE_PORT', 5000))
