import psycopg2, psycopg2.pool


class PgDatabaseHelper:
    def __init__(self, conn_string, schema):
        self._conn_string = conn_string
        self._schema = schema
        self._pool = psycopg2.pool.ThreadedConnectionPool(8, 64, conn_string)

    def get_similar_tables(self, table_name, schema_name=None):
        schema_clause = "" if schema_name is None else " AND schema = {0:s}".format(schema_name)
        query = """SELECT schema, name FROM {0:s}.tables WHERE name % '{1:s}{2:s}' 
        ORDER BY similarity(name, '{1:s}') DESC""".format(self._schema, table_name, schema_clause)
        rows = self._get_rows(query)
        return [{'schema': row[0], 'name': row[1]} for row in rows]

    def get_similar_columns(self, column_name, schema_name=None, table_name=None):
        if (schema_name is None and table_name is not None) or (schema_name is not None and table_name is None):
            raise RuntimeError("Check schema and table")
        if table_name is None:
            query = """SELECT name FROM {0:s}.columns WHERE name % '{1:s}' 
            ORDER BY similarity(name, '{1:s}') DESC""".format(
                self._schema, column_name)
        else:
            query = """SELECT c.name FROM {0:s}.columns AS c JOIN {0:s}.tables AS t ON t.id = c.table_id
             WHERE t.schema = '{1:s}' AND t.name = '{2:s}' AND c.name % '{3:s}' 
             ORDER BY similarity(c.name, '{3:s}') DESC""".format(self._schema, schema_name, table_name, column_name)
        rows = self._get_rows(query)
        return [row[0] for row in rows]

    def get_tables(self):
        query = "SELECT schema, name FROM {0:s}.tables ORDER BY name ASC".format(self._schema)
        rows = self._get_rows(query)
        return [{'schema': row[0], 'name': row[1]} for row in rows]

    def get_columns(self, schema_name, table_name):
        query = """SELECT c.name, c.data_type FROM {0:s}.columns AS c JOIN {0:s}.tables AS t ON t.id = c.table_id
            WHERE t.schema = '{1:s}' AND t.name = '{2:s}'
            ORDER BY name ASC""".format(self._schema, schema_name, table_name)
        rows = self._get_rows(query)
        return [{'name': row[0], 'type': row[1]} for row in rows]

    def get_max_word_similarity(self, word, text):
        query = "SELECT word_similarity('{0:s}', '{1:s}')".format(word, text)
        rows = self._get_rows(query)
        return [row[0] for row in rows]

    def get_foreign_keys(self):
        query = """SELECT
                    tc.table_schema, tc.table_name, kcu.column_name,
                    ccu.table_schema AS foreign_table_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name
                FROM
                    information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu USING (constraint_name)
                    JOIN information_schema.constraint_column_usage AS ccu USING (constraint_name)
                WHERE
                    tc.constraint_type = 'FOREIGN KEY';"""
        rows = self._get_rows(query)
        return [{'table_schema': row[0], 'table_name': row[1], 'column_name': row[2],
                 'foreign_table_schema': row[3], 'foreign_table_name': row[4], 'foreign_column_name': row[5]}
                for row in rows]

    def _get_rows(self, query):
        conn = self._pool.getconn()
        cursor = conn.cursor()
        cursor.execute(query)
        result = list([row for row in cursor])
        self._pool.putconn(conn)
        return result
