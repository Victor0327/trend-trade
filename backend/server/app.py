# -*- coding: UTF-8 -*-
import os
import logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
import json

from datetime import datetime

from flask import Flask, request, Response
from flask.helpers import make_response

from controller import bar, opportunities, symbol_data
from trade_opportunities_job import main as trade_opportunities_job

from utils.json import custom_json_handler
# 本地环境注释
# TODO: qcloud环境需要打开
import cron_job


app = Flask(__name__)

@app.route('/symbol_data', methods=['GET'])
def get_symbol_data():
    symbol_type = request.args.get('symbol_type')
    symbol = request.args.get('symbol')
    interval = request.args.get('interval')
    page = request.args.get('page')
    limit = request.args.get('limit')

    args = {
        'symbol_type': symbol_type,
        'symbol': symbol,
        'interval': interval,
        'page': page,
        'limit': limit
    }

    request_data = request.data

    data = symbol_data.get_symbol_data(args)
    resp = make_response()

    HTTP_STATUS_OK = 200
    CONTENT_TYPE_JSON = "application/json"
    DEFAULT_CONTENT_TYPE = CONTENT_TYPE_JSON + "; charset=utf-8"

    resp_data = {
        'code': 'success',
        'data': data
    }


    resp = Response(json.dumps(resp_data, default=custom_json_handler), status=200, content_type='application/json')
    return resp

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
