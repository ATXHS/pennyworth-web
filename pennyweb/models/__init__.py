import calendar
from datetime import date
from dateutil.relativedelta import relativedelta
from string import lower

import ldap3
import uuid
from refreshbooks import api
from flask import url_for
from pennyweb import app

AD_USER = app.config['AD_USER']
AD_PASSWD = app.config['AD_PASSWD']
SERVER_LIST = app.config['AD_SERVER_LIST']
AD_USE_TLS = app.config['AD_USE_TLS']
AD_USER_BASE_DN = app.config['AD_USER_BASE_DN']
AD_GROUP_BASE_DN = app.config['AD_GROUP_BASE_DN']

class ClientAlreadyExists(Exception):
    pass

class ADUserAlreadyExists(Exception):
    pass

class ADEmailAlreadyExists(Exception):
    pass

class ADAddFailed(Exception):
    pass

import logging
from ldap3.utils.log import set_library_log_activation_level, set_library_log_detail_level, ERROR, DEBUG, EXTENDED

if app.config['DEBUG']:
    logging.basicConfig(level=logging.DEBUG)
    set_library_log_detail_level(EXTENDED)
    set_library_log_activation_level(logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
    set_library_log_detail_level(ERROR)

# need a better name for this shit
class ActiveDirectoryClient(object):
    def __init__(self):
        self.server_pool = ldap3.ServerPool(
            servers=[ldap3.Server(s, use_ssl=AD_USE_TLS) for s in SERVER_LIST],
            pool_strategy=ldap3.POOLING_STRATEGY_FIRST,
            active=True)
        self.connection = ldap3.Connection(
            self.server_pool,
            user=AD_USER,
            password=AD_PASSWD,
            auto_bind=ldap3.AUTO_BIND_NO_TLS) # use_ssl=True above makes it use TLS, so we don't have to use the StartTLS command in the connection.
        self.connection.raise_exceptions = True

    def create_user(self, username, email, first_name, last_name):
        if self.email_taken(email):
            raise ADEmailAlreadyExists()
        elif self.username_taken(username):
            raise ADUserAlreadyExists()
        else:
            # more things go here
            cn = username
            dn = 'cn={},{}'.format(cn, AD_USER_BASE_DN)
            ok = self.connection.add(
                dn,
                [u'top', u'person', u'organizationalPerson', u'user'],
                 {'mail': email,
                 'sAMAccountName': username,
                 'distinguishedName': dn,
                 'givenName': first_name,
                 'sn': last_name,
                 'displayName': '{} {}'.format(first_name, last_name),
                 'cn': cn,
            })
            if not ok:
                raise ADAddFailed()
            app.logger.debug(self.connection.response)
            ok = self.connection.search(
                search_base=AD_USER_BASE_DN,
                search_filter='(sAMAccountName={})'.format(username),
                search_scope=ldap3.SUBTREE,
                attributes=["objectGUID"],
            )
            if not ok:
                app.logger.error('Got non-SUCCESS response: {}, last_error: {}'.format(ok, self.connection.last_error))
                app.logger.error('Last response: {}'.format(self.connection.response))
                raise ADAddFailed()
            return '{{{}}}'.format(uuid.UUID(bytes_le=self.connection.response[0]['attributes']['objectGUID'][0]))


    def username_taken(self, username):
        return self.connection.search(
            search_base=AD_USER_BASE_DN,
            search_filter='(sAMAccountName={})'.format(username),
            search_scope=ldap3.SUBTREE)

    def email_taken(self, email):
        return self.connection.search(
            search_base=AD_USER_BASE_DN,
            search_filter='(mail={})'.format(email),
            search_scope=ldap3.SUBTREE)

def get_client(debug=False):
    return api.TokenClient(
        app.config['FRESHBOOKS_URL'],
        app.config['FRESHBOOKS_TOKEN'],
        app.config['FRESHBOOKS_USER_AGENT'],
        request_encoder=api.logging_request_encoder if debug else api.default_request_encoder,
        response_decoder=api.logging_response_decoder if debug else api.default_response_decoder
    )


def create_invoice(form):
    ad = ActiveDirectoryClient()
    c = get_client()

    # Check if user exists in freshbooks
    response = c.client.list(folder='active', email=form.email.data)

    # If so, don't allow an invoice to be made
    if int(response.clients.attrib['total']) > 0:
        app.logger.debug(
            'Client already exists with email {0} (checked for {1})'.format(
                response.clients.client[0].email, form.email.data))
        raise ClientAlreadyExists()

    # Try to create user in active directory
    guid = ad.create_user(
        username=form.username.data, email=form.email.data,
        first_name=form.first_name.data, last_name=form.last_name.data)

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
            name='ATXDUES', unit_cost='95', quantity='1',
            description='$95 Dues for the month of ::month::\nID: {}'.format(guid)
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

treasurer@atxhackerspace.org
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
