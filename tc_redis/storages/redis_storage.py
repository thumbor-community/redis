# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta

from redis import RedisError
from thumbor.storages import BaseStorage
from thumbor.utils import logger

from tc_redis.utils import on_exception
from tc_redis.base_storage import RedisBaseStorage


class Storage(BaseStorage, RedisBaseStorage):
    def __init__(self, context, shared_client=True):
        """Initialize the RedisStorage

        :param thumbor.context.Context shared_client: Current context
        :param boolean shared_client: When set to True a singleton client will
                                      be used.
        """

        BaseStorage.__init__(self, context)
        RedisBaseStorage.__init__(self, context, "storage")
        self.shared_client = shared_client
        self.storage = self.get_storage()

    def on_redis_error(self, fname, exc_type, exc_value):
        """Callback executed when there is a redis error.

        :param string fname: Function name that was being called.
        :param type exc_type: Exception type
        :param Exception exc_value: The current exception
        :returns: Default value or raise the current exception
        """

        self.storage = None
        self.set_shared_storage(None)

        if self.context.config.REDIS_STORAGE_IGNORE_ERRORS is True:
            logger.error(f"[REDIS_STORAGE] {exc_value}")
            if fname == "_exists":
                return False
            return None
        else:
            raise exc_value

    def __key_for(self, url):
        return f"thumbor-crypto-{url}"

    def __detector_key_for(self, url):
        return f"thumbor-detector-{url}"

    @on_exception(on_redis_error, RedisError)
    async def put(self, path, image_bytes):
        storage = self.get_storage()
        storage.set(path, image_bytes)
        storage.expireat(
            path,
            datetime.now()
            + timedelta(seconds=self.context.config.STORAGE_EXPIRATION_SECONDS),
        )

    @on_exception(on_redis_error, RedisError)
    async def put_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return

        if not self.context.server.security_key:
            raise RuntimeError(
                "STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no "
                "SECURITY_KEY specified"
            )

        key = self.__key_for(path)
        self.get_storage().set(key, self.context.server.security_key)

    @on_exception(on_redis_error, RedisError)
    async def put_detector_data(self, path, data):
        key = self.__detector_key_for(path)
        self.get_storage().set(key, json.dumps(data))

    async def get_crypto(self, path):
        return self._get_crypto(path)

    @on_exception(on_redis_error, RedisError)
    def _get_crypto(self, path):
        if not self.context.config.STORES_CRYPTO_KEY_FOR_EACH_IMAGE:
            return None

        crypto = self.get_storage().get(self.__key_for(path))

        if not crypto:
            return None
        return crypto

    async def get_detector_data(self, path):
        return self._get_detector_data(path)

    @on_exception(on_redis_error, RedisError)
    def _get_detector_data(self, path):
        data = self.get_storage().get(self.__detector_key_for(path))

        if not data:
            return None
        return json.loads(data)

    async def exists(self, path):
        return self._exists(path)

    @on_exception(on_redis_error, RedisError)
    def _exists(self, path):
        return self.get_storage().exists(path)

    @on_exception(on_redis_error, RedisError)
    async def remove(self, path):
        self.get_storage().delete(path)

    async def get(self, path):
        @on_exception(self.on_redis_error, RedisError)
        def wrap():
            return self.get_storage().get(path)

        return wrap()
