SHELL := /usr/bin/env bash

PROM_IP ?= 192.168.1.110

.PHONY: fmt validate plan apply destroy-all deploy-all node-exporter-all prom-reconcile status

fmt:
	terraform fmt -recursive

validate:
	terraform validate

plan:
	terraform plan

apply:
	terraform apply -parallelism=1

destroy-all:
	terraform destroy

status:
	@echo "==> Inventory services:"
	@./scripts/inventory_list.py || true

node-exporter-all:
	./scripts/deploy-node-exporter-all.sh

prom-reconcile:
	./scripts/reconcile-prometheus.sh $(PROM_IP)

deploy-all: apply node-exporter-all prom-reconcile
	@echo "==> deploy-all complete"