import enum
from app import db
# from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Index, text, UniqueConstraint
from sqlalchemy.orm import relationship
# from sqlalchemy.schema import UniqueConstraint, text


class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.BigInteger, primary_key=True)
    request = db.Column(db.Text, nullable=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    session = db.Column(db.Text)
    result = relationship("Result", back_populates="request")

    def __init__(self, request, session):
        self.request = request
        self.session = session

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def __str__(self):
        return '<Request id=%s>' % self.id

    def to_dict(self):
        return {
            'id': self.id,
            'request': self.request
        }


class ReportTypeEnum(enum.Enum):
    table = 1
    graph = 2
    chart = 3

ReportTypeEnum2int = {
    ReportTypeEnum.table: 1,
    ReportTypeEnum.graph: 2,
    ReportTypeEnum.chart: 3
}


class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.BigInteger, primary_key=True)
    request_id = db.Column(db.BigInteger, db.ForeignKey('requests.id'))
    request = relationship("Request", back_populates="result")
    query = db.Column(db.Text, nullable=False)
    rate = db.Column(db.Float)
    report_type = db.Column(db.Enum(ReportTypeEnum), default=ReportTypeEnum.table)

    def __init__(self, request_id, query, rate, report_type):
        self.request_id = request_id
        self.query = query
        self.rate = rate
        self.report_type = report_type

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def __str__(self):
        return '<Request id=%s>' % self.id

    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'query': self.query,
            'rate': self.rate,
            'report_type': ReportTypeEnum2int[self.report_type]
        }


class Table(db.Model):
    __tablename__ = "tables"
    __table_args__ = (
        UniqueConstraint('schema', 'name', name="_schema_name_uc"),
        # Index('table_name_trgm_index',
        #       text('name gist_trgm_ops'),
        #       postgresql_using="gist")
    )

    id = db.Column(db.BigInteger, primary_key=True)
    schema = db.Column(db.Text)
    name = db.Column(db.Text, nullable=False)
    column = relationship("Column", back_populates="table")

    def __init__(self, schema, name):
        self.schema = schema
        self.name = name

    def __str__(self):
        return "%s.%s" % (self.schema, self.name)


class Column(db.Model):
    __tablename__ = "columns"
    __table_args__ = (
        UniqueConstraint('table_id', 'name', name="_table_name_uc"),
    )

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    data_type = db.Column(db.Text, nullable=False)  # TODO: change in ln2sql
    table_id = db.Column(db.BigInteger, db.ForeignKey("tables.id"))
    table = relationship("Table", back_populates="column")

    def __init__(self, name, date_type, table_id):
        self.name = name
        self.data_type = date_type
        self.table_id = table_id

    def __str__(self):
        return "%s %s" % (self.name, self.column_type)


# class ForeignKey(db.Model):
#     __tablename__ = "foreign_keys"
#     __table_args__ = (
#         UniqueConstraint('table_schema', 'table_name',
#                          'column_name', 'foreign_table_schema',
#                          'foreign_table_name', 'foreign_column_name'),
#     )
#
#     id = db.Column(db.BigInteger, primary_key=True)
#     table_schema = db.Column(db.Text),
#
#     table_name = db.Column(db.Text),
#     column_name = db.Column(db.Text),
#     foreign_table_schema = db.Column(db.Text),
#     foreign_table_name = db.Column(db.Text),
#     foreign_column_name = db.Column(db.Text)
#
#     def __str__(self):
#         return ""
