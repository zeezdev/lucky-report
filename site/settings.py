import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_DATABASE_URI = "postgresql://luckyreportuser:luckyreportuser@localhost/luckyreport"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LANG_STORE_PATH = "/home/zeez/work/APPLIEDTECH/ln2sql/ln2sql/lang_store/"


    # CONNECTION STRING OF DB FOR INDEXATION
    DBNAME = "zeezdev"
    DBUSER = "zeezdevuser"
    DBPASS = "88323003"
    DBHOST = "localhost"


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True