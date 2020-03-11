from flask import Flask, Response, request
from prometheus_client import generate_latest, Gauge, Histogram, Counter, Summary, CONTENT_TYPE_LATEST
from prometheus_flask_exporter import PrometheusMetrics

import os, time, sys, json, requests

VERSION="0.0.1b"
BOTID='Robotics'
BOTPWD='na'
OUTPUT_URL=os.environ['REPORT_URL']

app = Flask(__name__)
m = PrometheusMetrics(app=app)

@app.route('/alert/<string:room>', methods=['POST'])
def alert(room):
    alertinfo = request.json
    app.logger.debug(alertinfo)
    c = len(alertinfo['alerts'])
    app.logger.debug('There are ' + str(c) + ' alerts.')
    for alert in alertinfo['alerts']:
        json_data = {}
        json_data['to'] = room
        json_data['displayfromname'] = 'AlertManager Bot'
        json_data['from'] = BOTID
        json_data['password'] = BOTPWD
        json_data['type'] = 'meeting'
        if alert['status'] == "firing":
            app.logger.info('Firing WARNING Alert to ' + room)
            app.logger.info('WARNING: ' + alert['annotations']['description'])
            json_data['html'] = str('<span style="color: #ff0000;">WARNING</span>: ' + alert['annotations']['description'])
        else:
            app.logger.info('Firing RESOLVED Alert to ' + room)
            app.logger.info('RESOLVED: ' + alert['annotations']['description'])
            json_data['html'] = str('<span style="color: #008000;">RESOLVED:</span> ' + alert['annotations']['description'])
        app.logger.info('JSON: ' + json.dumps(json_data))
        response = requests.post(OUTPUT_URL, data=json.dumps(json_data))
        app.logger.info('Posted to: ' + OUTPUT_URL)
        app.logger.info('Response: ' + response.text)
    return "Ok."

@app.route('/notify/<string:room>', methods=['POST'])
def notify(room):
    alertinfo = request.json
    app.logger.debug(alertinfo)
    c = len(alertinfo['alerts'])
    app.logger.debug('There are ' + str(c) + ' alerts.')
    for alert in alertinfo['alerts']:
        json_data = {}
        json_data['to'] = room
        json_data['displayfromname'] = 'AlertManager Bot'
        json_data['from'] = BOTID
        json_data['password'] = BOTPWD
        json_data['type'] = 'meeting'
        if alert['status'] == "firing":
            app.logger.info('Firing NOTIFICATION Alert to ' + room)
            app.logger.info('NOTIFICATION: ' + alert['annotations']['description'])
            json_data['html'] = str('<span style="color: #0000ff;">NOTIFICATION</span>: ' + alert['annotations']['description'])
            app.logger.info('JSON: ' + json.dumps(json_data))
            response = requests.post(OUTPUT_URL, data=json.dumps(json_data))
            app.logger.info('Posted to: ' + OUTPUT_URL)
            app.logger.info('Response: ' + response.text)
    return "Ok."

@app.route('/metrics', methods=['GET'])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/', methods=['GET'])
def index():
    config = '<html><header><title>Webhook</title></header>'
    config += '<body><h1 align="center">TSM Robotics [' + VERSION + ']</h1><hr>'
    config += '<h2 align="left">Engine Usage Config:</h2>'
    config += '</body></html>'
    return config

@app.before_first_request
def onStartup():
    m.info('webhook_app_info', 'Application Info',
            version=VERSION,
            )
    app.logger.debug('onStartup')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
