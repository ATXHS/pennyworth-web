from pennyweb import app

from flask import flash, redirect, render_template, url_for
from flask.ext.wtf import Email, Form, Required, SelectField, TextField


class InvoiceForm(Form):
    first_name = TextField('first name', [Required()])
    last_name = TextField('last name', [Required()])
    email = TextField('email', [Required(), Email()])
    home_phone = TextField('home phone')
    mobile = TextField('mobile phone')

    # primary address
    p_street1 = TextField('address 1', [Required()])
    p_street2 = TextField('address 2')
    p_city = TextField('city', [Required()])
    p_state = TextField('state', [Required()])
    p_code = TextField('zip', [Required()])

    payment_type = SelectField('payment type', default='subscription',
                               choices=[('', ''), ('', '')])


@app.route('/', methods=('GET', 'POST'))
def index():
    form = InvoiceForm()
    if form.validate_on_submit():
        flash('Success!')
        return redirect(url_for('success'))
    return render_template('index.html', form=form)

@app.route('/success')
def success():
    return render_template('success.html')
