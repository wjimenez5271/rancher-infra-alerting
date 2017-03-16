import time
import logging
import json
import os
import requests
import socket

## Configuration
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 15))
SERVER_HOSTNAME = os.getenv("SERVER_HOSTNAME", "localhost")
SERVER_PORT = int(os.getenv("SERVER_PORT", 5050))
LOG_LEVEL = os.getenv("LOG_LEVEL",'DEBUG')


class RancherCheck(object):
    def __init__(self):
        self.name = ""
        self.description = ""
        self.last_eval = 0
        self.host = socket.gethostname()

    def eval(self):
        raise NotImplementedError

    def alert(self):
        try:
            URL = os.path.join("http://"+SERVER_HOSTNAME+":"+str(SERVER_PORT)+"/report_alert")
            resp = requests.post(URL,
                                 headers={'Content-type': 'application/json', 'Accept': 'text/plain'},
                                 data=json.dumps({"name": self.name,
                                                  "description": self.description,
                                                  "host": self.host
                                 }))
            log.debug(resp.text)
        except requests.exceptions.ConnectionError:
            log.error("Connection Error when communicating with server at {0}".format(URL))


class CheckKubeAPI(RancherCheck):
    def __init__(self):
        super(CheckKubeAPI, self).__init__()

        self.name = "CheckKubeAPI"
        self.description = "Assert K8 API is reachable and responds with a usable result"
        self.last_eval = ""

    def eval(self):
        r = requests.get('http://kubernetes.kubernetes.rancher.internal')
        if r.status_code != 200:
            log.info("Recieved the following non-200 response for check {0}: {1}".format(self.name, r.text))
            self.alert()


class CheckMetaData(RancherCheck):
    def __init__(self):
        super(CheckMetaData, self).__init__()
        self.name = "CheckMetaData"
        self.description = "Assert meta data servivce is reachable and responds with a usable result"
        self.last_eval = 0

    def eval(self):
        # do stuff
        r = requests.get('http://169.254.169.250')
        if r.status_code != 200:
            log.info("Recieved the following non-200 response for check {0}: {1}".format(self.name, r.text))
            self.alert()


class CheckEtcd(RancherCheck):
    def __init__(self):
        super(CheckEtcd, self).__init__()
        self.name = "CheckMetaData"
        self.description = "Assert meta data servivce is reachable and responds with a usable result"
        self.last_eval = 0

    def eval(self):
        r = requests.get('http://etcd.rancher.internal:2379/health')
        if r.status_code != 200:
            log.info("Recieved the following non-200 response for check {0}: {1}".format(self.name, r.text))
            self.alert()


class PseudoCheck(RancherCheck):
    def __init__(self):
        super(PseudoCheck, self).__init__()
        self.name = "PseudoCheck"
        self.description = "Asser the basic check and alerting workflow functions"
        self.last_eval = 0

    def eval(self):
        log.info('Simulating alert')
        self.alert()


class RancherMonitor(object):
    def __init__(self):
        self.checks = []

    def add_check(self, _check):
        self.checks.append(_check)

    def eval_chekcs(self):
        for check in self.checks:
            log.info("Evaluating check {0}".format(check.name))
            try:
                check.eval()
                check.last_eval = time.time()
            except Exception as e:
                log.exception(e)


def init_logger():
    global LOG_LEVEL
    log = logging.getLogger('infra-monitor-client')
    log.setLevel(LOG_LEVEL)
    log.propagate = False
    stderr_logs = logging.StreamHandler()
    stderr_logs.setLevel(getattr(logging, LOG_LEVEL))
    stderr_logs.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    log.addHandler(stderr_logs)
    return log


monitor = RancherMonitor()
monitor.add_check(PseudoCheck())
monitor.add_check(CheckEtcd())

if __name__ == '__main__':
    log = init_logger()
    log.info('Starting agent...')
    while True:
        monitor.eval_chekcs()
        log.debug('Sleeping...')
        time.sleep(POLL_INTERVAL)

