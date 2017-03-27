from flask import Flask, request, abort
import logging
import syslog_client
import os
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from slackclient import SlackClient
from sys import exit


SYSLOG_HOST = os.getenv("SYSLOG_HOST", "localhost")
BIND_PORT = int(os.getenv("BIND_PORT", 5050))
LOG_LEVEL = os.getenv("LOG_LEVEL",'DEBUG')
ALERT_TARGETS = os.getenv("ALERT_TARGETS", "syslog")
SLACK_TOKEN = os.getenv("SLACK_API_TOKEN", None)
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", None)

app = Flask(__name__)

active_targets = []


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
    log.info("Sending the following to syslog {0}".format(payload))
    sclient.warn(payload)


def write_to_slack(payload):
    sc = SlackClient(SLACK_TOKEN)
    log.info("Sending the following to Slack {0}".format(payload))

    sc.api_call(
        "chat.postMessage",
        username="Rancher Infrastructure Alerting",
        as_user=False,
        channel=SLACK_CHANNEL,
        text=payload
    )

# Map of available alert targets
avail_alert_targets = {"syslog": write_to_syslog,
                       "slack": write_to_slack
                       }


def setup_alert_targets():
    targets = ALERT_TARGETS.split(",")
    for t in targets:
        # test requirements for Slack
        if t.lower() == 'slack':
            if SLACK_TOKEN is None or SLACK_CHANNEL is None:
                log.error("Missing required config values for Slack API")
                exit(1)
        try:
            active_targets.append(avail_alert_targets[t.lower()])
            log.info("Registered {0} as alerting target".format(t.lower()))
        except KeyError:
            log.error('Specified target not found: {0}'.format(t))


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
    for target in active_targets:
        target(message)


@app.route("/report_alert", methods=['POST'])
def report_alert():
    """
    report monitoring alert
    :return:
    """
    if not request.json:
        log.error('received non-json data')
        abort(400)

    log.debug(request.json)
    handle_alert(request.json)
    return 'OK'


@app.route("/health", methods=['GET'])
def health():
    """
    health check endpoint for external service to monitor
    :return:
    """
    return 'OK'


if __name__ == "__main__":
    log = init_logger()
    sclient = syslog_client.Syslog(host=SYSLOG_HOST)

    # read user's config to get desired alert targets
    setup_alert_targets()

    log.info('Starting server')
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(BIND_PORT)
    IOLoop.instance().start()