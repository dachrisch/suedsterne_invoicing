from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired
from wtforms.widgets import Input


class MonthInput(Input):
    input_type = 'month'


class MonthField(DateField):
    widget = MonthInput()


class BillingMonthForm(FlaskForm):
    date = MonthField(u'Billing Month', validators=[DataRequired('please state month')], format="%Y-%m")
    submit = SubmitField('Submit')
