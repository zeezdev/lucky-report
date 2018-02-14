import enum
from app import db
# from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship


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