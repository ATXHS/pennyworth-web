pennyworth-web
=============

Web app for pennyworth

Changing the invoice amounts
----------------------------

1. Change the MEMBERSHIP_PRICE and/or AUTOPAY_DISCOUNT variables in the instance/pennyweb.cfg file on the server.
2. Restart the server by running:

   ```
   # supervisorctl stop pennyworth
   # supervisorctl start pennyworth
   ```

   Note: something is wrong with supervisorctl and it will not exit in a reasonable amount of time. It will stop and start the service relatively quickly, though. Just verify it is down and then back up by checking the site and then CTRL-C to kill the supervisorctl command once that is done

Setup
-----

1. Install pipenv
2. `cd /path/to/pennyworth-web`
3. `pipenv shell`
4. `pipenv install`
5. `python setup.py develop`
6. `mkdir instance`
7. `cp pennyweb/default_settings.py instance/pennyweb.cfg`

Running
-------

1. Make sure pennyweb virtualenv is activated (`pipenv shell`)
2. Make sure you are in the pennyworth-web directory
3. run `manage-pennyweb runserver`
