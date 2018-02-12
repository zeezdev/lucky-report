from flask import Blueprint, render_template, request, session, jsonify
# from flask_sqlalchemy_session import current_session

pages_app = Blueprint('pages_app', __name__)
from models import Request, Result, ReportTypeEnum
from app import db


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

    # TODO: Search work
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
    results.append(Result(request_obj.id,
                     "SELECT server_id, name, server_type FROM servers WHERE name LIKE 'a*'",
                     1.000, ReportTypeEnum.table))
    results.append(Result(request_obj.id,
                     "SELECT server_id, node_id, node_name, server_type FROM servers s, nodes n WHERE s,server_id = n.server_id GROUP BY server_type",
                     0.900, ReportTypeEnum.chart))
    results.append(Result(request_obj.id,
                     "SELECT server_id, node_id, node_name, server_type FROM servers s, nodes n WHERE s,server_id = n.server_id GROUP BY server_type ORDER BY s.server_name",
                     0.540, ReportTypeEnum.graph))
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

        results = [r.id for r in request_obj.result]
        result.update({
            'request_id': request_id,
            'results': results,
            'ok': 1
        })
    except (ValueError, TypeError):
        result['error'] = 'request_id bad value'
    except Exception as ex:
        result['error'] = 'unknown error'
        print("Error: %s" % str(ex))

    return jsonify(result)

