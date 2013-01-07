from flask import Flask
from flask.ext.debugtoolbar import DebugToolbarExtension

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('pennyweb.default_settings')
app.config.from_pyfile('pennyweb.cfg')

# Debug toolbar
toolbar = DebugToolbarExtension(app)

import pennyweb.views
