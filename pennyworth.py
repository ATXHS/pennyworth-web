from flask import Flask, render_template
from flask.ext.wtf import Email, Form, TextField, Required

app = Flask(__name__)
app.secret_key = 'jmnkovbdfhnvgr8vnioh389gvbh839b h'


class InvoiceForm(Form):
    first_name = TextField('first name', [Required()])
    last_name = TextField('last name', [Required()])
    email = TextField('email', [Required(), Email()])
    home_phone = TextField('home phone')
    mobile = TextField('mobile phone')

    # primary address
    p_street1 = TextField('address 1')
    p_street2 = TextField('address 2')
    p_city = TextField('city')
    p_state = TextField('state')
    p_code = TextField('zip')


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


if __name__ == '__main__':
    app.run(debug=True)
