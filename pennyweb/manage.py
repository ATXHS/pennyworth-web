from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from . import app
# from pennyweb.models import install_webhooks
from .models import db
from .models.freshbooks import get_all_clients
from .models.users import user_datastore
from .util import state_map

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


#@manager.command
# def install_hooks():
#    install_webhooks()

@manager.command
def pull_freshbooks():
    "Synchronize users from freshbooks into local DB"
    for client in get_all_clients():
        print client.first_name, client.last_name, client.email
        if user_datastore.get_user(client.email.text):
            continue
        user_datastore.create_user(
            freshbooks_id=client.client_id.pyval,
            first_name=client.first_name.text,
            last_name=client.last_name.text,
            nickname=client.username.text,
            email=client.email.text,
            active=True,

            home_phone=client.home_phone.text,
            cell_phone=client.mobile.text,

            address=client.p_street1.text,
            address2=client.p_street2.text,
            city=client.p_city.text,
            state=_state(client.p_state.text),
            zip_code=client.p_code.text
        )
        db.session.commit()


def _state(given):
    if given:
        try:
            return state_map[given.title()]
        except KeyError:
            if given.upper() in state_map.values():
                return given.upper()
    return None


def main():
    from datetime import datetime

    @app.before_first_request
    def create_user():
        db.create_all()
        user_datastore.create_user(email='user@user.com', password='password',
                                   confirmed_at=datetime.utcnow())
        db.session.commit()

    manager.run()

if __name__ == '__main__':

    main()
