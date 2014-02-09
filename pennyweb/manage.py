from flask_script import Manager

from . import app
# from pennyweb.models import install_webhooks
from .models import db
from .models.users import user_datastore

manager = Manager(app)


#@manager.command
# def install_hooks():
#    install_webhooks()


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
