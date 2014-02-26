from flask import Flask
from flask_dashed.admin import Admin

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('pennyweb.default_settings')
app.config.from_pyfile('pennyweb.cfg')
admin = Admin(app)

# IMPORTANT: These imports *must* be after the above initialization of
# the app variable because they circularly-import this package (which
# will only be initialized up to this point in the file) in order to
# access the app variable.
#
# See the "Circular Imports" section on this page:
# http://flask.pocoo.org/docs/patterns/packages/

from . import extensions
import pennyweb.views
