# Rancher Infrastructure Alerting 

A simple tool to monitor the core components of Rancher infrastructure.

*This is beta software and not intended for general consumption*

## Configuring 

configuration is done through environment variables

### Client

- POLL_INTERVAL - Time in seconds to sleep between polling cycles 
- SERVER_HOSTNAME - Hostname or IP address of alerting server to report to
- SERVER_PORT - Port alerting server is listening on
- LOG_LEVEL - Verbosity of logging for the process

### Server

- SYSLOG_HOST - Address of syslog server to send alerts to. Assumes port 514 and UDP 
- LOG_LEVEL - Verbosity of logging for the process
