test: unit

unit:
	@pytest --cov=tc_redis tests/ --asyncio-mode=strict --cov-report term-missing

setup:
	@pip install -Ue .[tests]

format:
	@black .