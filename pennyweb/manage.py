from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from . import app
# from pennyweb.models import install_webhooks
from .models import db
from .models.freshbooks import get_all_clients, get_client
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


@manager.command
def count_freshbooks():
    "Count number of recurring freshbooks profiles"
    line_types = set()
    count = 0
    for recurring in get_all_recurring(get_client()):
        for line in recurring.lines.line:
            if line.name in ('ATXDUES', 'FAMILY30', 'CORP50'):
                count += 1
            if str(line.name).startswith('1YEAR'):
                count += 1
            if str(line.name).startswith('1-YEAR'):
                count += 1
            line_types.add(line.name)
            # print line.name, line.description, line.unit_cost
    print count
    print line_types


def get_all_recurring(c, folder='active'):
    page = 0
    last_page = 1
    while page < last_page:
        page += 1
        res = c.recurring.list(folder=folder, page=page)
        last_page = int(res.recurrings.attrib['pages'])

        for recurring in res.recurrings.recurring:
            yield recurring


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
