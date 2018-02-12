from app import db
# from sqlalchemy.dialects.postgresql import JSON
# from sqlalchemy import BigInteger, Column, JSON, Text,


class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.BigInteger, primary_key=True)
    request = db.Column(db.Text, nullable=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    session = db.Column(db.Text)

    def __init__(self, request, session):
        self.request = request
        self.session = session

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def __str__(self):
        return '<id {}>'.format(self.id)


# class Result(db.Model):
#     __tablename__ = 'results'
#
#     id = db.Column(db.BigInteger, primary_key=True)
#     request = db.Column(db.Text, nullable=True)
#     created_on = db.Column(db.DateTime, server_default=db.func.now())
#     session = db.Column(db.Text)
#
#     def __init__(self, request, session):
#         self.request = request
#         self.session = session
#
#     def __repr__(self):
#         return '<id {}>'.format(self.id)
