# -*- coding: utf-8 -*-

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2014 PopKey martin@popkey.co

import time
from datetime import datetime, timedelta
from redis import Redis, RedisError
from tc_redis.utils import on_exception
from thumbor.result_storages import BaseStorage
from thumbor.utils import logger


class Storage(BaseStorage):

    storage = None

    '''start_time is used to calculate the last modified value when an item
    has no expiration date.
    '''
    start_time = None

    def __init__(self, context, shared_client=True):
        '''Initialize the RedisStorage

        :param thumbor.context.Context shared_client: Current context
        :param boolean shared_client: When set to True a singleton client will
                                      be used.
        '''

        BaseStorage.__init__(self, context)
        self.shared_client = shared_client
        self.storage = self.reconnect_redis()

        if not Storage.start_time:
            Storage.start_time = time.time()

    def get_storage(self):
        '''Get the storage instance.

        :return Redis: Redis instance
        '''

        if self.storage:
            return self.storage
        self.storage = self.reconnect_redis()

        return self.storage

    def reconnect_redis(self):
        '''Reconnect to redis.

        :return: Redis client instance
        :rettype: redis.Redis
        '''

        if self.shared_client and Storage.storage:
            return Storage.storage

        storage = Redis(
            port=self.context.config.REDIS_RESULT_STORAGE_SERVER_PORT,
            host=self.context.config.REDIS_RESULT_STORAGE_SERVER_HOST,
            db=self.context.config.REDIS_RESULT_STORAGE_SERVER_DB,
            password=self.context.config.REDIS_RESULT_STORAGE_SERVER_PASSWORD
        )

        if self.shared_client:
            Storage.storage = storage
        return storage

    def on_redis_error(self, fname, exc_type, exc_value):
        '''Callback executed when there is a redis error.

        :param string fname: Function name that was being called.
        :param type exc_type: Exception type
        :param Exception exc_value: The current exception
        :returns: Default value or raise the current exception
        '''

        if self.shared_client:
            Storage.storage = None
        else:
            self.storage = None

        if self.context.config.REDIS_RESULT_STORAGE_IGNORE_ERRORS is True:
            logger.error("Redis result storage failure: %s" % exc_value)

            return None
        else:
            raise exc_value

    def is_auto_webp(self):
        '''

        TODO This should be moved into the base storage class.
             It is shared with file_result_storage

        :return: If the file is a webp
        :rettype: boolean
        '''

        return self.context.config.AUTO_WEBP \
            and self.context.request.accepts_webp

    def get_key_from_request(self):
        '''Return a key for the current request url.

        :return: The storage key for the current url
        :rettype: string
        '''

        path = "result:%s" % self.context.request.url

        if self.is_auto_webp():
            path += '/webp'

        return path

    def get_max_age(self):
        '''Return the TTL of the current request.

        :returns: The TTL value for the current request.
        :rtype: int
        '''

        default_ttl = self.context.config.RESULT_STORAGE_EXPIRATION_SECONDS
        if self.context.request.max_age == 0:
            return self.context.request.max_age

        return default_ttl

    @on_exception(on_redis_error, RedisError)
    def put(self, bytes):
        '''Save to redis

        :param bytes: Bytes to write to the storage.
        :return: Redis key for the current url
        :rettype: string
        '''

        key = self.get_key_from_request()
        result_ttl = self.get_max_age()

        logger.debug(
            "[REDIS_RESULT_STORAGE] putting `{key}` with ttl `{ttl}`".format(
                key=key,
                ttl=result_ttl
            )
        )

        storage = self.get_storage()
        storage.set(key, bytes)

        if result_ttl > 0:
            storage.expireat(
                key,
                datetime.now() + timedelta(
                    seconds=result_ttl
                )
            )

        return key

    @on_exception(on_redis_error, RedisError)
    def get(self):
        '''Get the item from redis.'''

        key = self.get_key_from_request()
        result = self.get_storage().get(key)

        return result if result else None

    @on_exception(on_redis_error, RedisError)
    def last_updated(self):
        '''Return the last_updated time of the current request item

        :return: A DateTime object
        :rettype: datetetime.datetime
        '''

        key = self.get_key_from_request()
        max_age = self.get_max_age()

        if max_age == 0:
            return datetime.fromtimestamp(Storage.start_time)

        ttl = self.get_storage().ttl(key)

        if ttl >= 0:
            return datetime.now() - timedelta(
                seconds=(
                    max_age - ttl
                )
            )

        if ttl == -1:
            # Per Redis docs: -1 is no expiry, -2 is does not exists.
            return datetime.fromtimestamp(Storage.start_time)

        # Should never reach here. It means the storage put failed or the item
        # somehow does not exists anymore.
        return datetime.now()
