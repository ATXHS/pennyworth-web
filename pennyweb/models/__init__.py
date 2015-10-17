import calendar
from datetime import date
from dateutil.relativedelta import relativedelta
from os import environ
from string import lower

import ldap3
from refreshbooks import api
from flask import url_for
from pennyweb import app

ATXHS_AD_USER = environ.get('ATXHS_AD_USER')
ATXHS_AD_PASSWD = environ.get('ATXHS_AD_PASSWD')
ATXHS_SERVER_LIST = environ.get('ATXHS_AD_SERVER_LIST').split(",")
ATXHS_AD_USE_TLS = environ.get('ATXHS_AD_USE_TLS') == True
AD_USER_SEARCH_DN = 'ou=Batpass Users,dc=atxhs,dc=hack'
AD_GROUP_SEARCH_DN = 'ou=Batpass Groups,dc=atxhs,dc=hack'


# need a better name for this shit
class ActiveDirectoryClient(object):
    def __init__(self):
        self.server_pool = ldap3.ServerPool(ATXHS_SERVER_LIST,
                                            ldap3.POOLING_STRATEGY_ROUND_ROBIN,
                                            active=True)
        self.connection = ldap3.Connection(self.server_pool,
                                           user = ATXHS_AD_USER,
                                           password = ATXHS_AD_PASSWD,
                                           auto_bind = ldap3.AUTO_BIND_NO_TLS)
        self.connection.raise_exceptions = True
        self.connection.open()

    def create_aduser(self, user_hash):
        email = lower(user_hash['email'])
        username = lower(user_hash['username'])

        if self.email_taken(email) or self.username_taken(username):
            raise ADUserAlreadyExists
        else:
            # more things go here
            dn = 'cn=' + user_hash['username']
            dn = ','.join([dn, AD_USER_SEARCH_DN])
            self.connection.add(dn,
                                [u'top', u'person', u'organizationalPerson', u'user'],
                                {'mail': email,
                                 'sAMAccountName': username,
                                 'distinguishedName': dn})


    def username_taken(self, username):
        return self.connection.search(search_base=AD_USER_SEARCH_DN,
                               search_filter=''.join(['(sAMAccountName=', username, ')']),
                               search_scope=ldap3.SUBTREE)

    def email_taken(self, email):
        return self.connection.search(search_base=AD_USER_SEARCH_DN,
                               search_filter=''.join(['(mail=', email, ')']),
                               search_scope=ldap3.SUBTREE)

class ClientAlreadyExists(Exception):
    pass

class ADUserAlreadyExists(Exception):
    pass

def get_client(debug=False):
    return api.TokenClient(
        app.config['FRESHBOOKS_URL'],
        app.config['FRESHBOOKS_TOKEN'],
        app.config['FRESHBOOKS_USER_AGENT'],
        request_encoder=api.logging_request_encoder if debug else api.default_request_encoder,
        response_decoder=api.logging_response_decoder if debug else api.default_response_decoder
    )


def create_invoice(form):
    c = get_client()

    # Check if user exists in freshbooks
    response = c.client.list(folder='active', email=form.email.data)

    # If so, don't allow an invoice to be made
    if int(response.clients.attrib['total']) > 0:
        app.logger.debug(
            'Client already exists with email {0} (checked for {1})'.format(
                response.clients.client[0].email, form.email.data))
        raise ClientAlreadyExists()

    # If not, add client
    client = dict(
        first_name=form.first_name.data, last_name=form.last_name.data,
        email=form.email.data,
        p_street1=form.p_street1.data, p_street2=form.p_street2.data,
        p_city=form.p_city.data, p_state=form.p_state.data,
        p_code=form.p_code.data, p_country='United States',
    )
    if form.home_phone.data:
        client['home_phone'] = form.home_phone.data
    if form.mobile.data:
        client['mobile'] = form.mobile.data
    response = c.client.create(client=client)
    client_id = response.client_id

    # Add selected invoice type for client
    lines = [
        api.types.line(
            name='ATXDUES', unit_cost='85', quantity='1',
            description='$85 Dues for the month of ::month::'
        ),
        api.types.line(
            name='AUTOPAY', unit_cost='-25', quantity='1',
            description='$25 discount for Auto-Pay'
        ),
    ]
    invoice=dict(
        client_id=client_id,
        lines=lines,
        frequency='monthly',
        send_email='0',
        terms="""\
Your payment is due by the 1st of the month, late by the 10th of the month.

If you need more time, or have any issues please contact the Treasurer to make arrangements.

Martin Bogomolni
treasurer@atxhackerspace.org
(512) 553-3917
""")

    # Set recurring profile to send email and start on first of month
    response = c.recurring.create(recurring=invoice)
    recurring_id = response.recurring_id
    update_response = c.recurring.update(recurring=dict(recurring_id=recurring_id, send_email='1', date=(date.today() + relativedelta(months=1)).strftime('%Y-%m-01')))

    # Grab first invoice in set...
    response = c.invoice.list(recurring_id=recurring_id, status='draft')
    invoice = response.invoices.invoice[0]

    # ... And prorate the dues and autopay items, update record.
    prorate = month_left()
    prorated_lines = [api.types.line(name=l.name, unit_cost=l.unit_cost,
                                     quantity=prorate if l.name in ('ATXDUES', 'AUTOPAY') else l.quantity,
                                     description=l.description)
                      for l in invoice.lines.line]
    response = c.invoice.update(invoice=dict(invoice_id=invoice.invoice_id, lines=prorated_lines, notes='Amount prorated for remainder of month.'))

    # Nofity the invoicee now that its prorated.
    c.invoice.sendByEmail(invoice_id=invoice.invoice_id)
    return invoice.links.client_view

def month_left():
    today = date.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    left = (float(days_in_month) - (today.day - 1)) / days_in_month
    return '%.02f' % left
    

def install_webhooks():
    print 'installing hooks...'
    c = get_client()
    response = c.callback.create(callback=dict(
        event='payment.create',
        uri=url_for('freshbooks_webhook', _external=True)
    ))
    if response.attrib['status'] == 'ok':
        print 'webhook created successfully'
    else:
        print 'failed to add webhook'


def verify_callback(data):
    c = get_client()
    c.callback.verify(callback=dict(
        callback_id=data['object_id'],
        verifier=data['verifier']
    ))


def payment_callback(data):
    app.logger.debug(data)
    c = get_client()
    payment_id = data['object_id']
    response = c.payment.get(payment_id=payment_id)
    invoice_id = response.payment.get('invoice_id', None)
    if not invoice_id:
        return

    response = c.invoice.get(invoice_id=invoice_id)

    recurring_id = response.invoice.get('recurring_id', None)
    if not recurring_id:
        return

    response = c.recurring.get(recurring_id=recurring_id)

    if not hasattr(response.recurring, 'autobill'):
        discount_id = None
        for line in response.recurring.lines.line:
            if line.name == 'AUTOPAY':
                discount_id = line.line_id
                break

        if discount_id:
            response = c.recurring.lines.delete(
                recurring_id=recurring_id,
                line_id=discount_id
            )
