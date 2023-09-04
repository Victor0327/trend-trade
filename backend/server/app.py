# -*- coding: UTF-8 -*-
import os
import logging
import json

from datetime import datetime

from flask import Flask, request, Response
from flask.helpers import make_response

from controller import bar_controller

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

app = Flask(__name__)

@app.route('/trade/alert', methods=['GET', 'POST'])
def webhook_alert():
    logging.info('=====webhook_alert start====')
    logging.info(request.path)
    request_data = request.data

    data = bar_controller.get_bars(symbol="600030.SS", period="30d", interval="60m")



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

# Start the httpserver, "Developer Console" -> "Event Subscriptions", setting Request URL: https://domain/webhook/event
# startup event http server, port: 8089
if __name__ == '__main__':
    app.run(port=5002, host="0.0.0.0")
