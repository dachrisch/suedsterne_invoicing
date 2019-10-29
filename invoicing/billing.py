class CustomerBilling(object):
    @staticmethod
    def from_event(event):
        return CustomerBilling(event.customer).add(event)

    def __init__(self, customer):
        self.customer = customer
        self.activities = {}

    def add(self, event):
        self.__add_activity(event.action, event.date, event.price)
        if event.travel_expenses:
            self.__add_activity('Reisekosten', event.date, event.travel_expenses)

        return self

    def __add_activity(self, activity, date, price):
        if activity not in self.activities.keys():
            self.activities[activity] = {'days': [], 'price': price}

        self.activities[activity]['days'].append(date)

    def __eq__(self, other):
        if isinstance(other, CustomerBilling):
            return other.customer == self.customer
        return False

    def __hash__(self):
        return hash(self.customer)

    def __str__(self):
        return "CustomerBilling(customer=%s, activities=%s)" % (
            self.customer, ["%s: %s @ %s" % (
                str(activity), self.activities[activity]['days'], self.activities[activity]['price']) for
                            activity in self.activities.keys()])


class MonthlyBilling(object):
    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.customer_billings = set()

    def add(self, customer_billing):
        self.customer_billings.add(customer_billing)
        return self

    def __str__(self):
        return "MonthlyBilling(billings=%s)" % ", ".join(
            [str(customer_billing) for customer_billing in self.customer_billings])
