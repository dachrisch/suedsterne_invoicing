import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_dance.contrib.google import make_google_blueprint

from web.views import InvoiceView, HomeView


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


def create_ssl_context():
    certificate = os.getenv('SSL_CERT', None)
    key = os.getenv('SSL_KEY', None)
    if certificate and key:
        return certificate, key
    return 'adhoc'


if __name__ == "__main__":
    create_app().run(ssl_context=create_ssl_context(),
                     host=os.getenv('INVOICE_SERVICE_HOST', 'localhost'),
                     port=os.getenv('INVOICE_SERVICE_PORT', 5000))
