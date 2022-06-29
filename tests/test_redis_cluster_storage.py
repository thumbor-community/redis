# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from cmath import exp
from socket import getnameinfo
from unittest import IsolatedAsyncioTestCase

import redis
from redis.cluster import RedisCluster, ClusterNode
import pytest
from preggy import expect
from thumbor.context import Context
from thumbor.config import Config


from tc_redis.storages.redis_storage import Storage as RedisStorage
from tests.fixtures.storage_fixtures import IMAGE_URL, IMAGE_BYTES, get_server


class RedisDBContext(IsolatedAsyncioTestCase):
    def setUp(self):
        self.connection = RedisCluster(
            startup_nodes=list([ClusterNode("localhost", x) for x in range(6390, 6393)])
        )
        self.cfg = Config(
            REDIS_CLUSTER_STORAGE_STARTUP_INSTANCES="localhost:6390,localhost:6391,localhost:6392",
            REDIS_STORAGE_MODE="cluster",
        )
        self.storage = RedisStorage(
            Context(config=self.cfg, server=get_server("ACME-SEC"))
        )

    def test_should_be_instance_of_cluster(self):
        expect(str(self.storage.get_storage().get_nodes())).to_equal(
            "[[host=127.0.0.1,port=6390,name=127.0.0.1:6390,server_type=primary,redis_connection=Redis<ConnectionPool<Connection<host=127.0.0.1,port=6390,db=0>>>], [host=127.0.0.1,port=6391,name=127.0.0.1:6391,server_type=primary,redis_connection=Redis<ConnectionPool<Connection<host=127.0.0.1,port=6391,db=0>>>], [host=127.0.0.1,port=6392,name=127.0.0.1:6392,server_type=primary,redis_connection=Redis<ConnectionPool<Connection<host=127.0.0.1,port=6392,db=0>>>]]"
        )


class CanStoreImage(RedisDBContext):
    @pytest.mark.asyncio
    async def test_should_be_in_catalog(self):
        await self.storage.put(IMAGE_URL % 1, IMAGE_BYTES)

        topic = self.connection.get(IMAGE_URL % 1)

        expect(topic).not_to_be_null()
        expect(topic).not_to_be_an_error()


class KnowsImageExists(RedisDBContext):
    @pytest.mark.asyncio
    async def test_should_exist(self):
        await self.storage.put(IMAGE_URL % 9999, IMAGE_BYTES)
        topic = await self.storage.exists(IMAGE_URL % 9999)
        expect(topic).not_to_be_null()
        expect(topic).not_to_be_an_error()
        expect(topic).to_be_true()


class KnowsImageDoesNotExist(RedisDBContext):
    @pytest.mark.asyncio
    async def test_should_not_exist(self):
        topic = await self.storage.exists(IMAGE_URL % 10000)
        expect(topic).not_to_be_null()
        expect(topic).not_to_be_an_error()
        expect(topic).to_be_false()


class CanRemoveImage(RedisDBContext):
    @pytest.mark.asyncio
    async def test_should_not_be_in_catalog(self):
        await self.storage.put(IMAGE_URL % 10001, IMAGE_BYTES)
        await self.storage.remove(IMAGE_URL % 10001)
        topic = self.connection.get(IMAGE_URL % 10001)
        expect(topic).not_to_be_an_error()
        expect(topic).to_be_null()


class CanReRemoveImage(RedisDBContext):
    @pytest.mark.asyncio
    async def test_should_not_be_in_catalog(self):
        await self.storage.remove(IMAGE_URL % 10001)
        topic = self.connection.get(IMAGE_URL % 10001)
        expect(topic).not_to_be_an_error()
        expect(topic).to_be_null()


class CanGetImage(RedisDBContext):
    @pytest.mark.asyncio
    async def test_should_not_be_null(self):
        await self.storage.put(IMAGE_URL % 2, IMAGE_BYTES)
        topic = await self.storage.get(IMAGE_URL % 2)
        expect(topic).not_to_be_null()
        expect(topic).not_to_be_an_error()

    @pytest.mark.asyncio
    async def test_should_have_proper_bytes(self):
        await self.storage.put(IMAGE_URL % 2, IMAGE_BYTES)
        topic = await self.storage.get(IMAGE_URL % 2)
        expect(topic).to_equal(IMAGE_BYTES)


class CanRaiseErrors(RedisDBContext):
    def setUp(self):
        super().setUp()
        self.cfg = Config(
            REDIS_CLUSTER_STORAGE_STARTUP_INSTANCES="localhost:6390,localhost:6391,localhost:6392",
            REDIS_STORAGE_MODE="cluster",
            REDIS_STORAGE_IGNORE_ERRORS=False,
        )
        self.storage = RedisStorage(
            context=Context(config=self.cfg, server=get_server("ACME-SEC")),
            shared_client=False,
        )

    @pytest.mark.asyncio
    async def test_should_throw_an_exception(self):
        try:
            topic = await self.storage.exists(IMAGE_URL % 3)
        except Exception as redis_error:
            expect(redis_error).not_to_be_null()
            expect(redis_error).to_be_an_error_like(redis.RedisError)


class IgnoreErrors(RedisDBContext):
    def setUp(self):
        super().setUp()

        self.cfg = Config(
            REDIS_CLUSTER_STORAGE_STARTUP_INSTANCES="localhost:6390,localhost:6391,localhost:6392",
            REDIS_STORAGE_MODE="cluster",
            REDIS_STORAGE_IGNORE_ERRORS=True,
        )
        self.storage = RedisStorage(
            context=Context(config=self.cfg, server=get_server("ACME-SEC")),
            shared_client=False,
        )

    @pytest.mark.asyncio
    async def test_should_return_false(self):
        result = await self.storage.exists(IMAGE_URL % 3)
        expect(result).to_equal(False)
        expect(result).not_to_be_an_error()

    @pytest.mark.asyncio
    async def test_should_return_none(self):
        result = await self.storage.get(IMAGE_URL % 3)
        expect(result).to_equal(None)
        expect(result).not_to_be_an_error()


class RaisesIfInvalidConfig(RedisDBContext):
    @pytest.mark.asyncio
    async def test_should_be_an_error(self):
        config = Config(
            REDIS_CLUSTER_STORAGE_STARTUP_INSTANCES="localhost:6390,localhost:6391,localhost:6392",
            REDIS_STORAGE_MODE="cluster",
            STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True,
        )
        storage = RedisStorage(Context(config=config, server=get_server("")))
        await storage.put(IMAGE_URL % 4, IMAGE_BYTES)

        try:
            await storage.put_crypto(IMAGE_URL % 4)
        except Exception as error:
            expect(error).to_be_an_error_like(RuntimeError)
            expect(error).to_have_an_error_message_of(
                "STORES_CRYPTO_KEY_FOR_EACH_IMAGE can't be True if no "
                "SECURITY_KEY specified"
            )


class GettingCryptoForANewImageReturnsNone(RedisDBContext):
    @pytest.mark.asyncio
    async def test_should_be_null(self):
        config = Config(
            REDIS_CLUSTER_STORAGE_STARTUP_INSTANCES="localhost:6390,localhost:6391,localhost:6392",
            REDIS_STORAGE_MODE="cluster",
            STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True,
        )
        storage = RedisStorage(Context(config=config, server=get_server("ACME-SEC")))

        topic = await storage.get_crypto(IMAGE_URL % 9999)
        expect(topic).to_be_null()


class DoesNotStoreIfConfigSaysNotTo(RedisDBContext):
    @pytest.mark.asyncio
    async def test_should_be_null(self):
        await self.storage.put(IMAGE_URL % 5, IMAGE_BYTES)
        await self.storage.put_crypto(IMAGE_URL % 5)
        topic = await self.storage.get_crypto(IMAGE_URL % 5)
        expect(topic).to_be_null()


class CanStoreCrypto(RedisDBContext):
    def setUp(self):
        super().setUp()
        self.cfg = Config(
            REDIS_CLUSTER_STORAGE_STARTUP_INSTANCES="localhost:6390,localhost:6391,localhost:6392",
            REDIS_STORAGE_MODE="cluster",
            STORES_CRYPTO_KEY_FOR_EACH_IMAGE=True,
        )
        self.storage = RedisStorage(
            Context(config=self.cfg, server=get_server("ACME-SEC"))
        )

    @pytest.mark.asyncio
    async def test_should_not_be_null(self):
        await self.storage.put(IMAGE_URL % 6, IMAGE_BYTES)
        await self.storage.put_crypto(IMAGE_URL % 6)
        topic = await self.storage.get_crypto(IMAGE_URL % 6)
        expect(topic).not_to_be_null()
        expect(topic).not_to_be_an_error()

    @pytest.mark.asyncio
    async def test_should_have_proper_key(self):
        await self.storage.put(IMAGE_URL % 6, IMAGE_BYTES)
        await self.storage.put_crypto(IMAGE_URL % 6)
        topic = await self.storage.get_crypto(IMAGE_URL % 6)
        expect(topic).to_equal("ACME-SEC")


class CanStoreDetectorData(RedisDBContext):
    @pytest.mark.asyncio
    async def test_should_not_be_null(self):
        await self.storage.put(IMAGE_URL % 7, IMAGE_BYTES)
        await self.storage.put_detector_data(IMAGE_URL % 7, "some-data")
        topic = await self.storage.get_detector_data(IMAGE_URL % 7)
        expect(topic).not_to_be_null()
        expect(topic).not_to_be_an_error()

    @pytest.mark.asyncio
    async def test_should_equal_some_data(self):
        await self.storage.put(IMAGE_URL % 7, IMAGE_BYTES)
        await self.storage.put_detector_data(IMAGE_URL % 7, "some-data")
        topic = await self.storage.get_detector_data(IMAGE_URL % 7)
        expect(topic).to_equal("some-data")


class ReturnsNoneIfNoDetectorData(RedisDBContext):
    @pytest.mark.asyncio
    async def test_should_not_be_null(self):
        topic = await self.storage.get_detector_data(IMAGE_URL % 10000)
        expect(topic).to_be_null()


class RedisModeInvalid(RedisDBContext):
    def setUp(self):
        super().setUp()

        self.cfg = Config(
            REDIS_CLUSTER_STORAGE_STARTUP_INSTANCES="localhost:6390,localhost:6391,localhost:6392",
            REDIS_STORAGE_MODE="test",
        )
        self.ctx = Context(
            config=self.cfg,
            server=get_server("ACME-SEC"),
        )

    @pytest.mark.asyncio
    async def test_should_raises_attribute_error(self):
        with self.assertRaises(AttributeError) as error:
            RedisStorage(self.ctx)

        expect(str(error.exception)).to_equal(
            "Unknown value for REDIS_STORAGE_MODE test. See README for more information."
        )
