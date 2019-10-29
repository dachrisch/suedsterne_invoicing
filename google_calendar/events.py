# coding=utf-8

import dateutil.parser
import parse


class CalendarEvent(object):
    TEMPLATE = 'Kunde: '

    @staticmethod
    def from_json(json):
        customer = json['summary'].replace(CalendarEvent.TEMPLATE, '')
        date = dateutil.parser.parse(json['start'].get('dateTime', json['start'].get('date')))
        result = parse.parse("Action: {action}\nPrice: {price}\nTravel Expense: {travel_expense}",
                             json['description'])
        return CalendarEvent(customer, date, result['price'], result['action'], result['travel_expense'])

    def __init__(self, customer, date, price, action, travel_expense):
        self.customer = customer
        self.price = price
        self.date = date
        self.action = action
        self.travel_expenses = travel_expense
