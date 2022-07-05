# Redis storage adapters

Thumbor redis storage adapters.

## Installation

```bash
pip install tc_redis
```

## Configuration

To use redis as a storage or result storage some values must be configured in `thumbor.conf`

##### Redis Storage

###### Single Node
```python
STORAGE = "tc_redis.storages.redis_storage"

REDIS_STORAGE_IGNORE_ERRORS = True
REDIS_STORAGE_SERVER_PORT = 6379
REDIS_STORAGE_SERVER_HOST = "localhost"
REDIS_STORAGE_SERVER_DB = 0
REDIS_STORAGE_SERVER_PASSWORD = None
REDIS_STORAGE_MODE = "single_node"
```

###### Cluster
```python
STORAGE = "tc_redis.storages.redis_storage"

REDIS_STORAGE_IGNORE_ERRORS = True
REDIS_CLUSTER_STORAGE_STARTUP_INSTANCES = "localhost:6379,localhost:6380"
REDIS_STORAGE_SERVER_PASSWORD = None
REDIS_STORAGE_MODE = "cluster"
```

###### Sentinel
```python
STORAGE = "tc_redis.storages.redis_storage"

REDIS_STORAGE_IGNORE_ERRORS = True
REDIS_SENTINEL_STORAGE_INSTANCES = "localhost:26379,localhost:26380"
REDIS_SENTINEL_STORAGE_MASTER_INSTANCE = "redismaster"
REDIS_SENTINEL_STORAGE_MASTER_PASSWORD = "dummy"
REDIS_SENTINEL_STORAGE_PASSWORD = "dummy"
REDIS_SENTINEL_STORAGE_SOCKET_TIMEOUT = 1.0
REDIS_STORAGE_MODE = "sentinel"
```

##### Redis Result Storage

###### Single Node
```python
RESULT_STORAGE = "tc_redis.result_storages.redis_result_storage"

REDIS_RESULT_STORAGE_IGNORE_ERRORS = True
REDIS_RESULT_STORAGE_SERVER_PORT = 6379
REDIS_RESULT_STORAGE_SERVER_HOST = "localhost"
REDIS_RESULT_STORAGE_SERVER_DB = 0
REDIS_RESULT_STORAGE_SERVER_PASSWORD = None
REDIS_RESULT_STORAGE_MODE = "single_node"
```

###### Cluster
```python
RESULT_STORAGE = "tc_redis.result_storages.redis_result_storage"

REDIS_RESULT_STORAGE_IGNORE_ERRORS = True
REDIS_CLUSTER_RESULT_STORAGE_STARTUP_INSTANCES = "localhost:6379,localhost:6380"
REDIS_STORAGE_SERVER_PASSWORD = None
REDIS_RESULT_STORAGE_MODE = "cluster"
```

###### Sentinel
```python
RESULT_STORAGE = "tc_redis.result_storages.redis_result_storage"

REDIS_RESULT_STORAGE_IGNORE_ERRORS = True
REDIS_SENTINEL_RESULT_STORAGE_INSTANCES = "localhost:26379,localhost:26380"
REDIS_SENTINEL_RESULT_STORAGE_MASTER_INSTANCE = "redismaster"
REDIS_SENTINEL_RESULT_STORAGE_MASTER_PASSWORD = "dummy"
REDIS_SENTINEL_RESULT_STORAGE_PASSWORD = "dummy"
REDIS_SENTINEL_RESULT_STORAGE_SOCKET_TIMEOUT = 1.0
REDIS_RESULT_STORAGE_MODE = "sentinel"
```
## Contribute

To build tc_redis locally use

```bash
make setup
```

To run unit tests use

```bash
make test
```
