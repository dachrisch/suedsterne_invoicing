# coding=utf-8

import dateutil.parser
import parse


class CalendarTemplateError(KeyError):
    def __init__(self, message):
        KeyError.__init__(self, message)


class CalendarEvent(object):
    CUSTOMER_BILLING_TEMPLATE = 'Kunde: '
    TRAVEL_EXPENSE_TEMPLATE = "Action: {action}\nPrice: {price}\nTravel Expense: {travel_expense}"

    @staticmethod
    def from_json(json):
        customer = json['summary'].replace(CalendarEvent.CUSTOMER_BILLING_TEMPLATE, '')
        date = dateutil.parser.parse(json['start'].get('dateTime', json['start'].get('date')))
        if 'description' not in json:
            raise CalendarTemplateError('description missing: %s, %s' % (customer, date))
        result = parse.parse(CalendarEvent.TRAVEL_EXPENSE_TEMPLATE,
                             json['description'])
        if result:
            event = CalendarEvent(customer, date, result['price'], result['action'], result['travel_expense'])
        else:
            result = parse.parse("Action: {action}\nPrice: {price}", json['description'])
            event = CalendarEvent(customer, date, result['price'], result['action'], None)
        return event

    def __init__(self, customer, date, price, action, travel_expense):
        self.customer = customer
        self.price = price
        self.date = date
        self.action = action
        self.travel_expenses = travel_expense
