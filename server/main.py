from flask import Flask, request, abort
import logging
import syslog_client
import os
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


SYSLOG_HOST = os.getenv("SYSLOG_HOST", "localhost")
BIND_PORT = int(os.getenv("BIND_PORT", 5050))
LOG_LEVEL = os.getenv("LOG_LEVEL",'DEBUG')

app = Flask(__name__)


def init_logger():
    global LOG_LEVEL
    log = logging.getLogger('infra-monitor-server')
    log.setLevel(LOG_LEVEL)
    log.propagate = True
    stderr_logs = logging.StreamHandler()
    stderr_logs.setLevel(getattr(logging, LOG_LEVEL))
    stderr_logs.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    log.addHandler(stderr_logs)
    # Format tornado's logs
    logging.getLogger('tornado').addHandler(stderr_logs)
    logging.getLogger('tornado').setLevel(getattr(logging, LOG_LEVEL))

    return log


def write_to_syslog(payload):
    sclient.warn(payload)


def handle_alert(alert_struct):
    check_name = alert_struct['name']
    description = alert_struct['description']
    host = alert_struct['host']
    message = "Rancher Infrastructure Event Alarm - " \
              "The following check has failed on host {host}: {check_name}. Check Description: {check_desc}".format(
        host=host,
        check_name=check_name,
        check_desc=description
    )
    log.info("Sending the following to syslog {0}".format(message))
    write_to_syslog(message)


@app.route("/report_alert", methods=['POST'])
def report_alert():
    '''
    report monitoring alert
    :return:
    '''
    if not request.json:
        log.error('received non-json data')
        abort(400)

    log.debug(request.json)
    handle_alert(request.json)
    return 'OK'


@app.route("/health", methods=['GET'])
def health():
    '''
    health check endpoint for external service to monitor
    :return:
    '''
    return 'OK'

if __name__ == "__main__":
    log = init_logger()
    sclient = syslog_client.Syslog(host=SYSLOG_HOST)
    log.info('Starting server')
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(BIND_PORT)
    IOLoop.instance().start()