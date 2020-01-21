from common import init
from flask_script import Manager
from flask_migrate import MigrateCommand

application, migrate = init(testing=False, managing=True)

manager = Manager(application.app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()