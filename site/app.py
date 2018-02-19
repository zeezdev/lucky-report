import os
from flask import Flask
from flask.sessions import SessionInterface
from beaker.middleware import SessionMiddleware
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy_session import flask_scoped_session
from pages.views import pages_app


session_opts = {
    'session.type': 'ext:memcached',
    'session.url': '127.0.0.1:11211',
    'session.data_dir': './cache',
}


class BeakerSessionInterface(SessionInterface):
    def open_session(self, app, request):
        session = request.environ['beaker.session']
        return session

    def save_session(self, app, session, response):
        session.save()


def get_pg_connection_string(host, dbname, user, password):
    return "host=%s dbname=%s user=%s password=%s" % (host, dbname, user, password)


def get_tables(pg_cur):
    pg_cur.execute("""
    SELECT DISTINCT table_schema, table_name
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_schema NOT IN('information_schema', 'pg_catalog')
    """)
    return pg_cur.fetchall()


def get_columns(pg_cur):
    pg_cur.execute("""
    SELECT table_schema, table_name, column_name, data_type, ordinal_position
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE table_schema NOT IN('information_schema', 'pg_catalog')
    ORDER BY table_schema, table_name, ordinal_position, column_name
    """)
    return pg_cur.fetchall()

def get_foreign_keys(pg_cur):
    pg_cur.execute("""
    WITH db_foreign_keys AS
    (
        SELECT
            tc.table_schema AS table_schema, tc.table_name AS table_name, kcu.column_name AS column_name,
            ccu.table_schema AS foreign_table_schema, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name,
            MAX(kcu.position_in_unique_constraint) OVER (PARTITION BY kcu.constraint_name, kcu.table_schema, kcu.table_name) AS columns_in_fk
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu USING (constraint_name, table_schema, table_name)
            JOIN information_schema.constraint_column_usage AS ccu USING (constraint_name)
        WHERE
            tc.constraint_type = 'FOREIGN KEY'
    )

    SELECT DISTINCT table_schema, table_name, column_name, foreign_table_schema, foreign_table_name, foreign_column_name
    FROM db_foreign_keys
    WHERE columns_in_fk = 1;  -- no multicolumn FKs
    """)
    return pg_cur.fetchall()

def index_work_db(config, db):
    from models import Table, Column
    import psycopg2

    # clear old data
    db.session.query(Column).filter().delete()
    db.session.query(Table).filter().delete()

    # connect to db
    pg_conn = psycopg2.connect(
        get_pg_connection_string(
            config['DBHOST'],
            config['DBNAME'],
            config['DBUSER'],
            config['DBPASS']))

    cur = pg_conn.cursor()

    # find tables
    rows = get_tables(cur)
    tables = []
    for row in rows:
        table = Table(schema=row[0], name=row[1])
        tables.append(table)
        db.session.add(table)
    rows = None
    db.session.commit()  # save tables in db

    # find columns
    tables_names = [table.name for table in tables]
    rows = get_columns(cur)
    columns = []
    for row in rows:
        table = next((t for t in tables if t.schema == row[0] and t.name == row[1]), None)
        if table is not None:
            column = Column(name=row[2], data_type=row[3], table_id=table.id)
            columns.append(column)
            db.session.add(column)
    rows = None
    db.session.commit()  # save columns in db


# # application factory, see: http://flask.pocoo.org/docs/patterns/appfactories/
# def create_app(config_filename):
#     app = Flask(__name__)
#     app.config.from_object(config_filename)
#
#     # app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)
#     # app.session_interface = BeakerSessionInterface()
#     # SQLAlchemy
#     db = SQLAlchemy(app)
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
#     # import blueprints
#     from pages.views import pages_app
#
#     # register blueprints
#     app.register_blueprint(pages_app)
#
#     return app, db

app = Flask(__name__)
try:
    app_settings = os.environ['APP_SETTINGS']
except KeyError:
    app_settings = 'settings.DevelopmentConfig'
app.config.from_object(app_settings)

# Backer session
if int(os.environ.get('RUN_MIGRATION', 0)) == 0:
    app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)
    app.session_interface = BeakerSessionInterface()

# SQLAlchemy
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

index_work_db(app.config, db)

# import & register blueprints
app.register_blueprint(pages_app)

# engine = create_engine("postgresql://luckyreportuser:luckyreportuser@localhost/luckyreport")
# session_factory = sessionmaker(bind=engine)
# session = flask_scoped_session(session_factory, app)


if __name__ == "__main__":
    app.run()
