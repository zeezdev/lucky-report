#!/usr/local/env python

import sys
import time
import logging
import json  # for config parsing
import psycopg2
from elasticsearch import Elasticsearch


logger = logging.getLogger(__name__)
handler = logging.FileHandler("agent.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


es = Elasticsearch()


class Schema:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "%s" % self.name


class Column:
    def __init__(self, name, tp, max_length=None):
        self.name = name
        self.column_type = tp
        self.max_length = max_length

    def __str__(self):
        return "%s %s%s" % (self.name, self.column_type, "" if self.max_length is None else "[%s]" % self.max_length)


class Table:
    def __init__(self, name, schema="public"):
        self.name = name
        self.schema = schema
        self._columns = []

    def __str__(self):
        return "%s.%s" % (self.schema, self.name)

    def add_column(self, column):
        self._columns.append(column)


def get_tables(pg_cur):
    pg_cur.execute("""
    SELECT table_name, table_schema
    FROM information_schema.tables
    WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
    """)
    rows = pg_cur.fetchall()
    tables = [Table(row[0], row[1]) for row in rows]
    return tables


def get_columns_raw(pg_cur):
    pg_cur.execute("""
    SELECT t.table_schema, t.table_name, c.column_name, c.data_type, c.character_maximum_length, c.ordinal_position
    FROM information_schema.TABLES t
    JOIN information_schema.COLUMNS c
    ON t.table_name::text = c.table_name::text AND t.table_schema::text = c.table_schema::text
    WHERE
        t.table_schema::text NOT IN ('information_schema', 'pg_catalog')
    AND
        t.table_catalog::name = current_database()
    AND
        t.table_type::text = 'BASE TABLE'::text
    AND
        NOT "substring"(t.table_name::text, 1, 1) = '_'::text
    ORDER BY t.table_name, c.ordinal_position
    """)
    rows = pg_cur.fetchall()
    return rows


def get_pk_raw(pg_cur):
    pg_cur.execute("""
    SELECT t.table_schema, t.table_name, t.constraint_type, t.constraint_name, array_to_string(array_agg(c.column_name::text), ',') AS keys
    FROM information_schema.TABLE_CONSTRAINTS t
    JOIN information_schema.CONSTRAINT_COLUMN_USAGE c
    ON t.constraint_name = c.constraint_name
    WHERE
        t.table_schema::text NOT IN ('information_schema', 'pg_catalog')
    AND
        constraint_type IN('UNIQUE', 'PRIMARY KEY')
    AND
        t.table_schema = 'public'
    GROUP BY t.constraint_name, t.table_name, t.table_schema, t.constraint_type
    ORDER BY t.table_name, t.constraint_type
    """)
    rows = pg_cur.fetchall()
    return rows


def index_db(logger, config):
    logger.info("Start DB index")

    pg_conn = psycopg2.connect(
        get_pg_connection_string(
            config['dbhost'],
            config['dbname'],
            config['dbuser'],
            config['dbpass']))
    logger.info("Pg db connected")
    cur = pg_conn.cursor()

    logger.info("get_tables()")
    result = get_tables(cur)
    tables = {}
    for r in result:
        tables[(r.schema, r.name)] = r
    msg = "\n".join([str(t) for t in tables.values()])
    logger.info(msg)

    logger.info("get_columns()")
    columns = get_columns_raw(cur)
    for c in columns:
        if (c[0], c[1]) in tables:
            column = Column(c[2], c[3], c[4])
            logger.info("add column '%s' into table '%s'", column, tables[(c[0], c[1])])
            tables[(c[0], c[1])].add_column(column)
    # logger.info(columns)

    logger.info("get_pk_raw()")
    columns = get_pk_raw(cur)


    logger.info("DB index complete")


def get_pg_connection_string(host, dbname, user, password):
    return "host=%s dbname=%s user=%s password=%s" % (host, dbname, user, password)


def run():
    # TODO: using config
    config = {
        'dbhost': "127.0.0.1",
        'dbname': "zeezdev",
        'dbuser': "zeezdevuser",
        'dbpass': ""
    }
    global logger

    try:
        while True:
            try:
                index_db(logger, config)
            except KeyboardInterrupt:
                raise
            except Exception as ex:
                print("Error: %s" % str(ex))
            finally:
                time.sleep(60)
    except KeyboardInterrupt:
        logger.warn("Interrupted by user. Exit")
        exit(0)


if __name__ == "__main__":
    run()
