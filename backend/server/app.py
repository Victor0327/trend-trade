# -*- coding: UTF-8 -*-
import os
import logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
import json

from datetime import datetime

from flask import Flask, request, Response
from flask.helpers import make_response

from controller import bar, opportunities, symbol_data, symbols, position_calculate, trade_record
from trade_opportunities_job import main as trade_opportunities_job

from utils.json import custom_json_handler
# 本地环境注释
# TODO: qcloud环境需要打开
import cron_job


app = Flask(__name__)

# 交易记录
@app.route('/trade_record/strategy_requirement', methods=['GET'])
def get_strategy_requirement():
    args = {
        'strategy_id': request.args.get('strategy_id')
    }
    resp_data = {
        'code': 'success',
        'data': trade_record.get_strategy_requirement(args)
    }
    return Response(json.dumps(resp_data, default=custom_json_handler), status=200, content_type='application/json')

@app.route('/trade_record/strategy', methods=['GET'])
def get_strategy():
    resp_data = {
        'code': 'success',
        'data': trade_record.get_strategy()
    }
    return Response(json.dumps(resp_data, default=custom_json_handler), status=200, content_type='application/json')


@app.route('/trade_record/delete_data', methods=['POST'])
def delete_data():
    args = {
        'risk_amount_currency': request.json.get('risk_amount_currency'),
        'risk_amount': request.json.get('risk_amount'),
        'id': request.json.get('id')
    }

    resp_data = {
        'code': 'success',
        'data': trade_record.delete_trade_record(args)
    }

    return Response(json.dumps(resp_data, default=custom_json_handler), status=200, content_type='application/json')

@app.route('/trade_record/close_position', methods=['POST'])
def close_position():
    args = {
        'risk_amount_currency': request.json.get('risk_amount_currency'),
        'risk_amount': request.json.get('risk_amount'),
        'id': request.json.get('id'),
        'close_date': request.json.get('close_date'),
        'result': request.json.get('result'),
        'memo': request.json.get('memo'),
    }

    resp_data = {
        'code': 'success',
        'data': trade_record.close_position(args)
    }

    return Response(json.dumps(resp_data, default=custom_json_handler), status=200, content_type='application/json')

@app.route('/trade_record/open_position', methods=['POST'])
def open_position():
    args = {
        'risk_amount_currency': request.json.get('risk_amount_currency'),
        'risk_amount': request.json.get('risk_amount'),
        'open_date': request.json.get('open_date'),
        'symbol_type': request.json.get('symbol_type'),
        'symbol': request.json.get('symbol'),
        'strategy_id': request.json.get('strategy_id'),
        'risk': request.json.get('risk'),
        'memo': request.json.get('memo'),
        'strategy_requirement_performance_array': request.json.get('strategy_requirement_performance_array'),
    }

    resp_data = {
        'code': 'success',
        'data': trade_record.create_trade_record(args)
    }

    return Response(json.dumps(resp_data, default=custom_json_handler), status=200, content_type='application/json')

@app.route('/trade_record/cumulative_sum', methods=['GET'])
def cumulative_sum():
    args = {
        'risk_amount': request.args.get('risk_amount'),
        'risk_amount_currency': request.args.get('risk_amount_currency'),
        'strategy_id': request.args.get('strategy_id'),
    }
    resp_data = {
        'code': 'success',
        'data': trade_record.get_cumulative_sum(args)
    }
    return Response(json.dumps(resp_data, default=custom_json_handler), status=200, content_type='application/json')

@app.route('/trade_record/list', methods=['GET'])
def list_record():
    args = {
        'risk_amount': request.args.get('risk_amount'),
        'risk_amount_currency': request.args.get('risk_amount_currency'),
    }
    resp_data = {
        'code': 'success',
        'data': trade_record.get_trade_record(args)
    }
    return Response(json.dumps(resp_data, default=custom_json_handler), status=200, content_type='application/json')

# 仓位计算器

@app.route('/position_calculate', methods=['POST'])
def get_position_calculate():
    json_data = request.json

    args = {
        'symbol': json_data.get('symbol'),
        'symbol_type': json_data.get('symbol_type'),
        'entry_price': json_data.get('entry_price'),
        'sl_price': json_data.get('sl_price'),
        'tp_price': json_data.get('tp_price'),
        'risk_amount': json_data.get('risk_amount'),
        'margin_level': json_data.get('margin_level'),
    }

    data = position_calculate.calculate(args)
    resp = make_response()

    resp_data = {
        'code': 'success',
        'data': data
    }

    resp = Response(json.dumps(resp_data, default=custom_json_handler), status=200, content_type='application/json')
    return resp


@app.route('/symbols', methods=['GET'])
def get_symbols():
    type = request.args.get('type')

    args = {
        'type': type,
    }

    data = symbols.get_symbols(args)
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
