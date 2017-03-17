build:
	docker build -t wjimenez5271/rancher-infra-alerting-client client && docker build -t wjimenez5271/rancher-infra-alerting-server server

push:
	docker push wjimenez5271/rancher-infra-alerting-client && docker push wjimenez5271/rancher-infra-alerting-server
