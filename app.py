import os

from dateutil.parser import parse
from flask import Flask, render_template
from flask import request

from google_calendar.service import GoogleCalendarService
from invoicing.billing import MonthlyBillingGenerator

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        date = parse("%s-%s-01" % (request.form.get('year'), request.form['month']))

        billing = MonthlyBillingGenerator.with_service(GoogleCalendarService()).generate_billing(date.year, date.month)

        return render_template('invoicing.html', billing=billing)

    return '''<form method="POST">
                  Year: <input type="text" name="year"><br>
                  Month: <input type="text" name="month"><br>
                  <input type="submit" value="Generate"><br>
              </form>'''


if __name__ == "__main__":
    app.run(host=os.getenv('INVOICE_SERVICE_HOST', '0.0.0.0'),
            port=os.getenv('INVOICE_SERVICE_PORT', 5000))
