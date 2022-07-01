REDIS_CONTAINER := redis-test redis-sentinel-test redis-cluster-test

test: run-redis wait-healthy-cluster unit stop-redis

unit:
	@pytest --cov=tc_redis tests/ --asyncio-mode=strict --cov-report term-missing

setup:
	@pip install -Ue .[tests]
	@pre-commit install

format:
	@pre-commit run --all-files

run-redis:
	@docker-compose up -d $(REDIS_CONTAINER)

stop-redis:
	@docker-compose stop $(REDIS_CONTAINER)

wait-healthy-cluster:
	@./tests/fixtures/redis-cluster/wait-healthy-cluster-in-container.sh
