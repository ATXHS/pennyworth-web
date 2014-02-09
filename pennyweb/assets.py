from . import app
from flask.ext.assets import Environment, Bundle

assets = Environment(app)

css = Bundle(
    'css/normalize.css',
    'css/foundation.css',

    filters='cssmin',
    output='public/css/combined.css'
)

js_top = Bundle(
    'js/vendor/modernizr.js',

    filters='jsmin', output='public/js/top.js'
)

js_bottom = Bundle(
    'js/vendor/jquery.js',
    'js/vendor/fastclick.js',
    'js/foundation/foundation.js',
    'js/foundation/foundation.abide.js',
    'js/foundation/foundation.accordion.js',
    'js/foundation/foundation.alert.js',
    'js/foundation/foundation.clearing.js',
    'js/foundation/foundation.dropdown.js',
    'js/foundation/foundation.equalizer.js',
    'js/foundation/foundation.interchange.js',
    'js/foundation/foundation.joyride.js',
    'js/foundation/foundation.magellan.js',
    'js/foundation/foundation.offcanvas.js',
    'js/foundation/foundation.orbit.js',
    'js/foundation/foundation.reveal.js',
    'js/foundation/foundation.tab.js',
    'js/foundation/foundation.tooltip.js',
    'js/foundation/foundation.topbar.js',

    filters='jsmin',
    output='public/js/bottom.js'
)

assets.register('css', css)
assets.register('js_top', js_top)
assets.register('js_bottom', js_bottom)
