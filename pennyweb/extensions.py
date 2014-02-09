from . import app
from . import assets
from flask.ext.debugtoolbar import DebugToolbarExtension

# Debug toolbar
toolbar = DebugToolbarExtension(app)
