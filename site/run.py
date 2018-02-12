#!/usr/bin/env python

import os


from app import create_app
try:
    app_settings = os.environ['APP_SETTINGS']
except KeyError:
    app_settings = 'settings.DevelopmentConfig'
app, db = create_app(app_settings)


if __name__ == "__main__":
    app.run()
