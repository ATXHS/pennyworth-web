from flask.ext.script import Manager

from pennyweb import app
from pennyweb.models import install_webhooks

manager = Manager(app)


@manager.command
def install_hooks():
    install_webhooks()


def main():
    manager.run()

if __name__ == '__main__':
    main()
