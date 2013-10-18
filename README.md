pennyworth-web
=============

Web app for pennyworth


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
