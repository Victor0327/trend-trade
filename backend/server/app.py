# -*- coding: UTF-8 -*-
import os
import logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
import json

from datetime import datetime

from flask import Flask, request, Response
from flask.helpers import make_response

from controller import bar, opportunities
from trade_opportunities_job import main as trade_opportunities_job
import cron_job


app = Flask(__name__)

@app.route('/symbol_candle_data/<string:symbol>', methods=['GET', 'POST'])
def symbol_candle_data(symbol):
    period = request.args.get('period')
    interval = request.args.get('interval')
    request_data = request.data

    data = bar.get_bars(symbol=symbol, period=period, interval=interval)



    resp = make_response()

    HTTP_STATUS_OK = 200
    CONTENT_TYPE_JSON = "application/json"
    DEFAULT_CONTENT_TYPE = CONTENT_TYPE_JSON + "; charset=utf-8"

    resp_data = {
        'code': 'success',
        'data': data
    }


    resp = Response(json.dumps(resp_data), status=200, content_type='application/json')
    return resp

@app.route('/ops/<string:create_date>/list', methods=['GET'])
def ops_list(create_date):
    page = request.args.get('page')
    limit = request.args.get('limit')

    args = {
        'create_date': create_date,
        'page': page,
        'limit': limit
    }

    list, count = opportunities.get_opportunities_by_create_date(args)



    resp = make_response()

    HTTP_STATUS_OK = 200
    CONTENT_TYPE_JSON = "application/json"
    DEFAULT_CONTENT_TYPE = CONTENT_TYPE_JSON + "; charset=utf-8"

    resp_data = {
        'code': 'success',
        'data': {
            'list': list,
            'count': count
        }
    }


    resp = Response(json.dumps(resp_data), status=200, content_type='application/json')
    return resp

@app.route('/market_scan', methods=['POST'])
def market_scan():

    # TODO:


    resp = make_response()

    HTTP_STATUS_OK = 200
    CONTENT_TYPE_JSON = "application/json"
    DEFAULT_CONTENT_TYPE = CONTENT_TYPE_JSON + "; charset=utf-8"

    resp_data = {
        'code': 'success',
        'data': data
    }


    resp = Response(json.dumps(resp_data), status=200, content_type='application/json')
    return resp


if __name__ == '__main__':
    app.run(port=5004, host="0.0.0.0")
