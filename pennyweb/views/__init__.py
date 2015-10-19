from pennyweb import app
from pennyweb.models import create_invoice, ADUserAlreadyExists,\
    ADEmailAlreadyExists, ADAddFailed, ClientAlreadyExists, verify_callback,\
    payment_callback

from flask import flash, redirect, request, render_template, url_for
from flask_wtf import Form, RecaptchaField
from wtforms import TextField
from wtforms.validators import DataRequired, Email, Regexp, Length


class InvoiceForm(Form):
    # The Basics
    username = TextField(
        'username *', [
            DataRequired(),
            Regexp(r'[a-zA-Z0-9][\w.]+', message='Username can only contain a-z, A-Z, 0-9, ".", and "_". Cannot start with "." or "_".'),
            Length(min=3, max=20),
        ])
    first_name = TextField('first name *', [DataRequired()])
    last_name = TextField('last name *', [DataRequired()])
    email = TextField('email *', [DataRequired(), Email()])
    home_phone = TextField('home phone')
    mobile = TextField('mobile phone')

    # Primary Address
    p_street1 = TextField('address 1 *', [DataRequired()])
    p_street2 = TextField('address 2')
    p_city = TextField('city *', [DataRequired()])
    p_state = TextField('state *', [DataRequired()])
    p_code = TextField('zip *', [DataRequired()])

    recaptcha = RecaptchaField()


@app.route('/', methods=('GET', 'POST'))  # Receive form data and validate
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
        except ADUserAlreadyExists:
            flash('The specified username already exists in our system. '
                  'Please choose a different username.')
            return render_template('index.html', form=form)
        except ADEmailAlreadyExists:
            flash('The specified email already exists in our system. '
                  'Contact treasurer@atxhackerspace.org.')
            return render_template('index.html', form=form)
        except ADAddFailed:
            flash('There was an unexpected error adding your user account. '
                  'Please contact treasurer@atxhackerspace.org.')
            return render_template('index.html', form=form)

    return render_template('index.html', form=form)


@app.route('/success')  # Woo, invoice created!
def success():
    invoice_url = request.args.get('invoice')
    return render_template('success.html', invoice_url=invoice_url)


@app.route('/freshbooks_webhook', methods=('POST',))  # Freshbooks callback
def freshbooks_webhook():
    name = request.form.get('name')
    if name == 'callback.verify':
        verify_callback(request.form)
    elif name == 'payment.create':
        payment_callback(request.form)
    return 'ok'
