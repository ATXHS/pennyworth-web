from datetime import datetime
from refreshbooks import api
from flask import url_for
from pennyweb import app


def get_client():
    return api.TokenClient(
        app.config['FRESHBOOKS_URL'],
        app.config['FRESHBOOKS_TOKEN'],
        app.config['FRESHBOOKS_USER_AGENT'],
    )


class ClientAlreadyExists(Exception):
    pass


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
    month = datetime.now().strftime('%B')
    lines = [
        api.types.line(
            name='ATXDUES', unit_cost='75', quantity='1',
            description='$75 Dues for the month of {0}'.format(month)
        )
    ]
    invoice=dict(
        client_id=client_id,
        lines=lines,
        frequency='monthly',
        send_email='1',
        terms="""\
Your payment is due by the 1st of the month, late by the 10th of the month.

If you need more time, or have any issues please contact the Treasurer to make arrangements.

Martin Bogomolni
treasurer@atxhackerspace.org
(512) 553-3917
""")
    response = c.recurring.create(recurring=invoice)


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
    c = get_client()
    recurring_id = data['object_id']
    response = c.recurring.get(recurring_id=20)

    if hasattr(response.recurring, 'autobill'):
        response = c.recurring.lines.add(
            recurring_id=recurring_id,
            lines=[api.types.line(
                name='AUTOPAY', unit_cost='-25', quantity='1',
                description='$25 discount for Auto-Pay'
            )]
        )
