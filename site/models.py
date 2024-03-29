import enum
import os

from sqlalchemy import Index, text, UniqueConstraint, Column as Cl, BigInteger, Text, DateTime, ForeignKey as Fk, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import now


if int(os.environ.get('RUN_MIGRATION', 0)) != 0:
    # FIXME: dirty hack for migration!
    from app import db
    Base = db.Model  # use for migrate
else:
    Base = declarative_base()


class Request(Base):
    __tablename__ = 'requests'

    id = Cl(BigInteger, primary_key=True)
    request = Cl(Text, nullable=True)
    created_on = Cl(DateTime, server_default=now())
    session = Cl(Text)
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


class Result(Base):
    __tablename__ = 'results'

    id = Cl(BigInteger, primary_key=True)
    request_id = Cl(BigInteger, Fk('requests.id'))
    request = relationship("Request", back_populates="result")
    query = Cl(Text, nullable=False)
    rate = Cl(Float)
    report_type = Cl(Enum(ReportTypeEnum), default=ReportTypeEnum.table)

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


class Table(Base):
    __tablename__ = "tables"
    __table_args__ = (
        UniqueConstraint('schema', 'name', name="_schema_name_uc"),
        Index('table_name_trgm_index',
              text('name gist_trgm_ops'),
              postgresql_using="gist")
    )

    id = Cl(BigInteger, primary_key=True)
    schema = Cl(Text)
    name = Cl(Text, nullable=False)
    column = relationship("Column", back_populates="table")

    def __init__(self, schema, name):
        self.schema = schema
        self.name = name

    def __str__(self):
        return "%s.%s" % (self.schema, self.name)


class Column(Base):
    __tablename__ = "columns"
    __table_args__ = (
        UniqueConstraint('table_id', 'name', name="_table_name_uc"),
    )

    id = Cl(BigInteger, primary_key=True)
    name = Cl(Text, nullable=False)
    data_type = Cl(Text, nullable=False)  # TODO: change in ln2sql
    table_id = Cl(BigInteger, Fk("tables.id"))
    table = relationship("Table", back_populates="column")

    # fk = relationship("ForeignKey", back_populates="column")
    # ffk = relationship("ForeignKey", back_populates="foreign_column")

    def __init__(self, name, data_type, table_id):
        self.name = name
        self.data_type = data_type
        self.table_id = table_id

    def __str__(self):
        return "%s %s" % (self.name, self.column_type)


class ForeignKey(Base):
    __tablename__ = "foreign_keys"
    __table_args__ = (
        UniqueConstraint('name', 'column_id', 'foreign_column_id'),
    )

    id = Cl(BigInteger, primary_key=True)
    name = Cl(Text,  nullable=False)

    column_id = Cl(BigInteger, Fk("columns.id"))
    foreign_column_id = Cl(BigInteger, Fk("columns.id"))

    column = relationship("Column", foreign_keys=[column_id])
    foreign_column = relationship("Column", foreign_keys=[foreign_column_id])

    def __init__(self, name, column_id, foreign_column_id):
        self.name = name
        self.column_id = column_id
        self.foreign_column_id = foreign_column_id

    def __str__(self):
        return '"%s" FOREIGN KEY (column_name) REFERENCES table_name(column_name)' % self.name
