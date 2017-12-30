.PHONY: redis-cli
redis-cli:
	redis-cli -u $(REDISCLOUD_URL)

.PHONY: pg-cli
pg-cli:
	pgcli $(DATABASE_URL)