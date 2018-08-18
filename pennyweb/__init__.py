from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('pennyweb.default_settings')
app.config.from_pyfile('pennyweb.cfg')

if app.config['PROXY_FIX']:
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)

# Debug toolbar
toolbar = DebugToolbarExtension(app)

import pennyweb.views
