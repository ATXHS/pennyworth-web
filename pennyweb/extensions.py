from . import app
from . import assets
from flask.ext.debugtoolbar import DebugToolbarExtension
from flask.ext.mail import Mail

toolbar = DebugToolbarExtension(app)
mail = Mail(app)
