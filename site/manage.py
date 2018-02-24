#!/usr/bin/env python

import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


os.environ['RUN_MIGRATION'] = '1'  # little hack for disable backer session


from app import app, db
# from models import *


app.config.from_object(os.environ.get('APP_SETTINGS', 'settings.DevelopmentConfig'))

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
