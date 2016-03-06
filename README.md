pennyworth-web
=============

Web app for pennyworth

Changing the invoice amounts
----------------------------

1. Change the MEMBERSHIP_PRICE and/or AUTOPAY_DISCOUNT variables in the instance/pennyweb.cfg file on the server.
2. Restart the server by running:

   ```
   # supervisortctl stop pennyworth
   # supervisorctl start pennyworth
   ```

   Note: something is wrong with supervisorctl and it will not exit in a reasonable amount of time. It will stop and start the service relatively quickly, though. Just verify it is down and then back up by checking the site and then CTRL-C to kill the supervisorctl command once that is done

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
