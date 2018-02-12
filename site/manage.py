import os
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand


os.environ['RUN_MIGRATION'] = '1'  # little hack for disable backer session


from app import app, db


app.config.from_object(os.environ.get('APP_SETTINGS', 'settings.DevelopmentConfig'))

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
