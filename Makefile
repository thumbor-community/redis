test: unit

unit:
	@pytest --cov=tc_redis tests/ --asyncio-mode=strict

setup:
	@pip install -Ue .[tests]

format:
	@black .