pennyworth-web
=============

Web app for pennyworth

Changing the invoice amounts
----------------------------

1. Change the values in the `create_invoice` function in
[pennyweb/models/\__init__.py](pennyweb/models/__init__.py). Be sure to change the `unit_cost` value
**and** the description to match.
2. Change the prices mentioned in the HTML in
[pennyweb/templates/index.html](pennyweb/templates/index.html) to match.


Setup
-----

1. Install virtualenv and virtualenv-wrapper
2. mkvirtualenv pennyweb (in the future "workon pennyweb")
3. cd /path/to/pennyworth-web
3. pip install -r requirements.txt
4. python setup.py develop
5. mkdir instance
6. cp pennyweb/default_settings.py instance/pennyweb.cfg

Running
-------

1. Make sure pennyweb virtualenv is activated ("workon pennyweb")
2. Make sure you are in the pennyworth-web directory
3. run "manage-pennyweb runserver"
