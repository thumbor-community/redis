# Redis storage adapters

[![Circle CI](https://circleci.com/gh/thumbor-community/redis.svg?style=svg)](https://circleci.com/gh/thumbor-community/redis)

Thumbor redis storage adapters.

## Installation

`pip install tc_redis`

## Configuration

To use redis as a storage or result storage some values must be configured in `thumbor.conf`

##### Redis Storage
```
STORAGE='tc_redis.storages.redis_storage'

REDIS_STORAGE_IGNORE_ERRORS = True
REDIS_STORAGE_SERVER_PORT = 6379
REDIS_STORAGE_SERVER_HOST = 'localhost'
REDIS_STORAGE_SERVER_DB = 0
REDIS_STORAGE_SERVER_PASSWORD = None
```

##### Redis Result Storage

```
RESULT_STORAGE='tc_redis.result_storages.redis_result_storage'

REDIS_RESULT_STORAGE_IGNORE_ERRORS = True
REDIS_RESULT_STORAGE_SERVER_PORT = 6379
REDIS_RESULT_STORAGE_SERVER_HOST = 'localhost'
REDIS_RESULT_STORAGE_SERVER_DB = 0
REDIS_RESULT_STORAGE_SERVER_PASSWORD = None
```
