from flask import Blueprint, render_template, request, session, jsonify
# from flask_sqlalchemy_session import current_session

pages_app = Blueprint('pages_app', __name__)
from models import Request, Result, ReportTypeEnum
from app import db, app
from ln2sql import Ln2sql


def translate(user_request):
    ln2sql = Ln2sql(
        database_path="/home/user/Documents/dd.sql",
        language_path="/home/user/work/ln2sql3/ln2sql/lang_store/english.csv",
        database_connection_string=app.config['WORK_DATABASE_URI'],
        # json_output_path=args.json_output,
        # thesaurus_path=args.thesaurus,
        # stopwords_path=args.stopwords,
    ).get_query(user_request)
    return ln2sql


@pages_app.route('/')
def index():
    context = {}

    request_id = request.values.get('request_id')
    if request_id is not None:
        request_id = int(request_id)
        # TODO: find in DB
        context['request_id'] = request_id

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

    # for r in t:
    if isinstance(t, str):
        results.append(Result(request_obj.id,
                              t,
                              1.000, ReportTypeEnum.table))
    else:
        for r in t:
            results.append(Result(request_obj.id,
                                  r,
                                  1.000, ReportTypeEnum.table))


    # results.append(Result(request_obj.id,
    #                  "SELECT server_id, name, server_type FROM servers WHERE name LIKE 'a*'",
    #                  1.000, ReportTypeEnum.table))
    # results.append(Result(request_obj.id,
    #                  "SELECT server_id, node_id, node_name, server_type FROM servers s, nodes n WHERE s,server_id = n.server_id GROUP BY server_type",
    #                  0.900, ReportTypeEnum.chart))
    # results.append(Result(request_obj.id,
    #                  "SELECT server_id, node_id, node_name, server_type FROM servers s, nodes n WHERE s,server_id = n.server_id GROUP BY server_type ORDER BY s.server_name",
    #                  0.540, ReportTypeEnum.graph))
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


@pages_app.route('/api/results/<result_id>')
def api_result_detail(result_id):
    result = {
        'ok': 0
    }
    try:
        result_obj = db.session.query(Result).filter_by(id=int(result_id)).first()
        result['result'] = result_obj.to_dict()
    except Exception as ex:
        print("Error: %s" % str(ex))
        return jsonify({'ok': 0, 'error': "server error"})

    return jsonify(result)
