from pennyweb import app
from pennyweb.models import create_invoice, ClientAlreadyExists,\
    verify_callback, payment_callback

from flask import flash, redirect, request, render_template, url_for
from flask.ext.wtf import Email, Form, Required, TextField


class InvoiceForm(Form):
    first_name = TextField('first name *', [Required()])
    last_name = TextField('last name *', [Required()])
    email = TextField('email *', [Required(), Email()])
    home_phone = TextField('home phone')
    mobile = TextField('mobile phone')

    # primary address
    p_street1 = TextField('address 1 *', [Required()])
    p_street2 = TextField('address 2')
    p_city = TextField('city *', [Required()])
    p_state = TextField('state *', [Required()])
    p_code = TextField('zip *', [Required()])


@app.route('/', methods=('GET', 'POST'))
def index():
    form = InvoiceForm()
    if form.validate_on_submit():
        try:
            invoice_url = create_invoice(form)
            flash('Success!')
            return redirect(url_for('success', invoice=invoice_url))
        except ClientAlreadyExists:
            flash('The specified email address already exists in our system. '
                  'Contact treasurer@atxhackerspace.org.')
            return render_template('index.html', form=form)

    return render_template('index.html', form=form)


@app.route('/success')
def success():
    invoice_url = request.args.get('invoice')
    return render_template('success.html', invoice_url=invoice_url)


@app.route('/freshbooks_webhook', methods=('POST',))
def freshbooks_webhook():
    name = request.form.get('name')
    if name == 'callback.verify':
        verify_callback(request.form)
    elif name == 'payment.create':
        payment_callback(request.form)
    return 'ok'
