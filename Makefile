export NAME?=whereismyfamily
export NAMESPACE?=whereismyfamily
export COLO:=$(shell kubectx -c)

.PHONY: apply
apply:
	@cat k8s.yml | envsubst | kubectl apply -n ${NAMESPACE} -f -
	@cat secrets.yml | envsubst | kubectl apply -n ${NAMESPACE} -f -

.PHONY: delete
delete:
	@cat k8s.yml | envsubst | kubectl delete -n ${NAMESPACE} -f -
	@cat secrets.yml | envsubst | kubectl delete -n ${NAMESPACE} -f -

.PHONY: deploy
deploy:
	kubectl rollout restart deployment/${NAME} && kubectl rollout status deployment/${NAME}

.PHONY: redis-cli
redis-cli:
	redis-cli -u $(REDISCLOUD_URL)

.PHONY: pg-cli
pg-cli:
	pgcli $(DATABASE_URL)