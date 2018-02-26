import os
import re

from .constants import Color
from .table import Table
from .pg_database_helper import PgDatabaseHelper


class Database:

    def __init__(self, database_connection_string):
        self.tables = []
        self.thesaurus_object = None
        self.database_helper = PgDatabaseHelper(database_connection_string)
        self.foreign_key_cache = dict()
        self.reverse_foreign_key_cache = dict()

    def set_thesaurus(self, thesaurus):
        self.thesaurus_object = thesaurus

    def get_number_of_tables(self):
        return len(self.tables)

    def get_tables(self):
        return self.tables

    def get_column_with_this_name(self, name):
        for table in self.tables:
            for column in table.get_columns():
                if column.name == name:
                    return column


    def get_similar_tables(self, table_name, schema_name=None):
        similar_tables = self.database_helper.get_similar_tables(table_name, schema_name)
        # similar_tables += self.thesaurus_object.get_synonyms_of_a_word(table_name)  # TODO: synonims?
        return similar_tables

    def get_similar_columns(self, column_name, schema_name=None, table_name=None):
        similar_columns = self.database_helper.get_similar_columns(column_name, schema_name, table_name)
        # similar_columns += self.thesaurus_object.get_synonyms_of_a_word(column_name)  # TODO: synonims?
        return similar_columns

    def get_full_similar_columns(self, column_name):
        return self.database_helper.get_full_similar_columns(column_name)

    def get_max_word_similarity(self, word, text):  # TODO: some library to do this without DB
        return float(self.database_helper.get_max_word_similarity(word, text)[0])

    def get_table_by_name(self, table_name):
        for table in self.tables:
            if table.full_name == table_name:
                return table

    def get_tables_into_dictionary(self):
        data = {}
        for table in self.tables:
            data[table.full_name] = []
            for column in table.get_columns():
                data[table.full_name].append(column.name)
        return data

    def get_primary_keys_by_table(self):
        data = {}
        for table in self.tables:
            data[table.full_name] = table.get_primary_keys()
        return data

    def get_foreign_keys_by_table(self):
        data = {}
        for table in self.tables:
            data[table.full_name] = table.get_foreign_keys()
        return data

    def get_primary_keys_of_table(self, table_name):
        for table in self.tables:
            if table.full_name == table_name:
                return table.get_primary_keys()

    def get_primary_key_names_of_table(self, table_name):
        for table in self.tables:
            if table.full_name == table_name:
                return table.get_primary_key_names()

    def get_foreign_keys_of_table(self, table_name):
        for table in self.tables:
            if table.full_name == table_name:
                return table.get_foreign_keys()

    def get_foreign_key_names_of_table(self, table_name):
        for table in self.tables:
            if table.full_name == table_name:
                return table.get_foreign_key_names()

    def get_foreign_tables_of_table(self, table_name):
        return self.foreign_key_cache.get(table_name)

    def get_tables_referenced_by(self, table_name):
        return self.reverse_foreign_key_cache.get(table_name)

    def add_table(self, table):
        self.tables.append(table)

    def cache_foreign_key(self, table_name, foreign_table_name):
        if self.foreign_key_cache.get(table_name) is None:
            self.foreign_key_cache[table_name] = set()
            self.foreign_key_cache[table_name].add(foreign_table_name)
        else:
            self.foreign_key_cache[table_name].add(foreign_table_name)

        if self.reverse_foreign_key_cache.get(foreign_table_name) is None:
            self.reverse_foreign_key_cache[foreign_table_name] = set()
            self.reverse_foreign_key_cache[foreign_table_name].add(table_name)
        else:
            self.reverse_foreign_key_cache[foreign_table_name].add(table_name)

    @staticmethod
    def _generate_path(path):
        cwd = os.path.dirname(__file__)
        filename = os.path.join(cwd, path)
        return filename

    def load(self, path):
        with open(self._generate_path(path)) as f:
            content = f.read()
            tables_string = [p.split(';')[0] for p in content.split('CREATE') if ';' in p]
            for table_string in tables_string:
                if 'TABLE' in table_string:
                    table = self.create_table(table_string)
                    self.add_table(table)
            alter_tables_string = [p.split(';')[0] for p in content.split('ALTER') if ';' in p]
            for alter_table_string in alter_tables_string:
                if 'TABLE' in alter_table_string:
                    self.alter_table(alter_table_string)

    def load_from_db(self):
        for db_table in self.database_helper.get_tables():
            table = Table()
            table.schema = db_table['schema']
            table.name = db_table['name']
            for column_definition in self.database_helper.get_columns(table.schema, table.name):
                table.add_column(column_definition['name'], self.predict_type(column_definition['type']), None)
            self.add_table(table)

        for key in self.database_helper.get_foreign_keys():
            full_table_name = '{0:s}.{1:s}'.format(key['table_schema'], key['table_name'])
            full_foreign_table_name = '{0:s}.{1:s}'.format(key['foreign_table_schema'], key['foreign_table_name'])
            table = self.get_table_by_name(full_table_name)
            if table is not None:
                table.add_foreign_key(key['column_name'], full_foreign_table_name, key['foreign_column_name'])
                self.cache_foreign_key(full_table_name, full_foreign_table_name)

    def predict_type(self, string):
        if 'int' in string.lower():
            return 'int'
        elif 'char' in string.lower() or 'text' in string.lower():
            return 'string'
        elif 'date' in string.lower() or 'time' in string.lower():
            return 'date'
        else:
            return 'unknown'

    def create_table(self, table_string):
        lines = table_string.split("\n")
        table = Table()
        for line in lines:
            if 'TABLE' in line:
                table_name = re.search("`(\w+)`", line)
                table.name = table_name.group(1)
                if self.thesaurus_object is not None:
                    table.equivalences = self.thesaurus_object.get_synonyms_of_a_word(table.name)
            elif 'PRIMARY KEY' in line:
                primary_key_columns = re.findall("`(\w+)`", line)
                for primary_key_column in primary_key_columns:
                    table.add_primary_key(primary_key_column)
            else:
                column_name = re.search("`(\w+)`", line)
                if column_name is not None:
                    column_type = self.predict_type(line)
                    if self.thesaurus_object is not None:
                        equivalences = self.thesaurus_object.get_synonyms_of_a_word(column_name.group(1))
                    else:
                        equivalences = []
                    table.add_column(column_name.group(1), column_type, equivalences)
        return table

    def alter_table(self, alter_string):
        lines = alter_string.replace('\n', ' ').split(';')
        for line in lines:
            if 'PRIMARY KEY' in line:
                table_name = re.search("TABLE `(\w+)`", line).group(1)
                table = self.get_table_by_name(table_name)
                primary_key_columns = re.findall("PRIMARY KEY \(`(\w+)`\)", line)
                for primary_key_column in primary_key_columns:
                    table.add_primary_key(primary_key_column)
            elif 'FOREIGN KEY' in line:
                table_name = re.search("TABLE `(\w+)`", line).group(1)
                table = self.get_table_by_name(table_name)
                foreign_keys_list = re.findall("FOREIGN KEY \(`(\w+)`\) REFERENCES `(\w+)` \(`(\w+)`\)", line)
                for column, foreign_table, foreign_column in foreign_keys_list:
                    table.add_foreign_key(column, foreign_table, foreign_column)

    def print_me(self):
        for table in self.tables:
            print('+-------------------------------------+')
            print("| %25s           |" % (table.name.upper()))
            print('+-------------------------------------+')
            for column in table.columns:
                if column.is_primary():
                    print("| 🔑 %31s           |" % (Color.BOLD + column.name + ' (' + column.get_type() + ')' + Color.END))
                elif column.is_foreign():
                    print("| #️⃣ %31s           |" % (Color.ITALIC + column.name + ' (' + column.get_type() + ')' + Color.END))
                else:
                    print("|   %23s           |" % (column.name + ' (' + column.get_type() + ')'))
            print('+-------------------------------------+\n')
