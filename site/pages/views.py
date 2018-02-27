import os
import random
from flask import Blueprint, render_template, request, jsonify
# from flask_sqlalchemy_session import current_session
import psycopg2

pages_app = Blueprint('pages_app', __name__)
from models import (Request, Result, ReportTypeEnum, ReportTypeEnum2int, ForeignKey, Column, Table)
from app import db, app
from ln2sql import Ln2sql


def translate(user_request):
    ln2sql = Ln2sql(
        language_path=os.path.join(app.config['LANG_STORE_PATH'], "english.csv"),
        database_connection_string=app.config['SQLALCHEMY_DATABASE_URI'],
        # json_output_path=args.json_output,
        # thesaurus_path=args.thesaurus,
        stopwords_path=os.path.join(app.config['LANG_STORE_PATH'], "..", "stopwords", "english.txt"),
    ).get_query(user_request)
    return ln2sql


@pages_app.route('/')
def index():
    context = {}

    request_id = request.values.get('request_id')
    if request_id is not None:
        request_id = int(request_id)
        request_obj = db.session.query(Request).filter_by(id=request_id).first()
        # TODO: find in DB
        context['request_id'] = request_id
        context['request_text'] = request_obj.request

    # try:
    #     ses_key = session['value']
    # except KeyError:
    #     ses_key = 'Save in session'
    #     session['value'] = ses_key
    #     session.save()
    # print("Session: %s" % ses_key)

    return render_template('pages/index.html', **context)


@pages_app.route('/about/')
def about():
    return render_template('pages/about.html')


@pages_app.route('/results/')
def result():
    try:
        result_id = request.values.get('id')
    except AttributeError:
        raise

    context = {
        'result_id': int(result_id)
    }
    print("id=%s" % result_id)
    return render_template('pages/result.html', **context)


def get_numeric_types(cur):
    q = """
    select oid, typname, typcategory from pg_type where typcategory in ('N')
    """
    cur.execute(q)
    rows = cur.fetchall()
    return [int(row[0]) for  row in rows]


NUMERIC = None


def execute_query(cur, query, limit=False):
    global NUMERIC
    if NUMERIC is None:
        NUMERIC = get_numeric_types(cur)
    print("numeric types oid: %s" % str(NUMERIC))

    if limit:
        query = "%s LIMIT 1" % query
    cur.execute(query)
    columns = [column[0] for column in cur.description]
    all_numeric = all(column.type_code in NUMERIC for column in cur.description[1:])

    rows = cur.fetchall()
    return columns, rows, all_numeric


def resolve_report_type_rnd(sql):
    return random.choice(list(ReportTypeEnum))


def resolve_report_type(cur, query):
    # execute query on working DB
    columns, _, all_numeric = execute_query(cur, query, limit=True)

    if all_numeric and len(columns) == 2:
        return ReportTypeEnum.chart  # pie
    elif all_numeric and len(columns) > 2:
        return ReportTypeEnum.graph

    return ReportTypeEnum.table


# API


@pages_app.route('/api/request')
def api_request():
    """Send user's search request"""
    request_text = request.values.get('request')
    result = {
        'ok': 1,
        'request_id': -1
    }

    # create request_id in DB
    try:
        session_key = request.cookies.get('beaker.session.id')
        # session_key = request.cookies.get('sessionid')

        request_obj = Request(
            request=request_text,
            session=session_key
        )
        db.session.add(request_obj)
        db.session.commit()
        print("Created %s" % str(request_obj))
        result['request_id'] = request_obj.id
    except Exception as ex:
        print(ex)

    # associate all found results with this request_id
    results = []
    t = []
    try:
        t = translate(request_text)
    except Exception as ex:
        print("Translation failed: %s" % str(ex))

    pg_conn = psycopg2.connect(
        get_pg_connection_string(
            app.config['DBHOST'],
            app.config['DBNAME'],
            app.config['DBUSER'],
            app.config['DBPASS']))
    cur = pg_conn.cursor()

    if t and isinstance(t, str):
        t = t.strip().replace('\n', ' ').replace('[1m', '').replace('[0m', '').replace('OOV', "'OOV' OR 1 = 1")
        t = t.split(';')

    results_count = float(len(t))
    for i, r in enumerate(t):
        if r:
            results.append(Result(request_obj.id,
                                  r,
                                  results_count - float(i),
                                  resolve_report_type(cur, r)))

    for r in results:
        db.session.add(r)
    db.session.commit()

    return jsonify(result)


@pages_app.route('/api/results')
def api_results():
    result = {
        'ok': 0,
        'request_id': None,
        # 'results': [1,2,3]
    }
    request_id = request.values.get('request_id')
    try:
        request_id = int(request_id)
        # request_obj = current_session.query(Request).filter_by(id=request_id).first()
        request_obj = db.session.query(Request).filter_by(id=request_id).first()

        results = [r.to_dict() for r in request_obj.result]
        result.update({
            'request_id': request_id,
            'results': results,
            'ok': 1
        })
    except (ValueError, TypeError) as ex:
        print("Type error: %s" % str(ex))
        result['error'] = 'request_id bad value'
    except Exception as ex:
        result['error'] = 'unknown error'
        print("Error: %s" % str(ex))

    try:
        js = jsonify(result)
    except Exception as ex:
        print(ex)
        result['ok'] = 0
        result['error'] = 'server error'
        return result

    return js


def get_pg_connection_string(host, dbname, user, password):
    return "host=%s dbname=%s user=%s password=%s" % (host, dbname, user, password)


@pages_app.route('/api/results/<result_id>')
def api_result_detail(result_id):
    result = {
        'ok': 0
    }
    try:
        result_obj = db.session.query(Result).filter_by(id=int(result_id)).first()
        result['result'] = result_obj.to_dict()
        result['request_text'] = result_obj.request.request
        result['request_id'] = result_obj.request.id

        # execute query on working DB
        pg_conn = psycopg2.connect(
            get_pg_connection_string(
                app.config['DBHOST'],
                app.config['DBNAME'],
                app.config['DBUSER'],
                app.config['DBPASS']))

        cur = pg_conn.cursor()
        columns, rows, all_numeric = execute_query(cur, result['result']['query'])

        result['data'] = rows
        result['columns'] = columns
        if all_numeric and len(columns) == 2:
            result['result']['report_type'] = ReportTypeEnum2int[ReportTypeEnum.chart]  # pie
        elif all_numeric and len(columns) > 2:
            result['result']['report_type'] = ReportTypeEnum2int[ReportTypeEnum.graph]
        else:
            result['result']['report_type'] = ReportTypeEnum2int[ReportTypeEnum.table]

        result['ok'] = 1
    except Exception as ex:
        print("Error: %s" % str(ex))
        return jsonify({'ok': 0, 'error': "server error"})

    return jsonify(result)
