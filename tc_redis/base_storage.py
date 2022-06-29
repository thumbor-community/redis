# -*- coding: utf-8 -*-

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2014 PopKey <martin@popkey.co>
# Copyright (c) 2022 Raphael Rossi <raphael.vieira.rossi@gmail.com>

from redis import Redis, Sentinel
from redis.cluster import RedisCluster, ClusterNode

SINGLE_NODE = "single_node"
CLUSTER = "cluster"
SENTINEL = "sentinel"


class RedisBaseStorage:

    single_node_storage = None
    cluster_storage = None
    sentinel_storage = None

    def __init__(self, context, storage_type):
        self.storage = None
        self.context = context
        self.storage_type = storage_type

        self.storage_values = {
            "storage": {
                "db": self.context.config.get("REDIS_STORAGE_SERVER_DB"),
                "host": self.context.config.get("REDIS_STORAGE_SERVER_HOST"),
                "instances": self.context.config.get(
                    "REDIS_CLUSTER_STORAGE_STARTUP_INSTANCES" if self.context.config.get("REDIS_STORAGE_MODE") == CLUSTER else "REDIS_SENTINEL_STORAGE_INSTANCES"
                ),
                "master_instance": self.context.config.get(
                    "REDIS_SENTINEL_STORAGE_MASTER_INSTANCE"
                ),
                "master_db": self.context.config.get(
                    "REDIS_SENTINEL_STORAGE_MASTER_DB", 0
                ),
                "master_password": self.context.config.get(
                    "REDIS_SENTINEL_STORAGE_MASTER_PASSWORD"
                ),
                "password": self.context.config.get("REDIS_STORAGE_SERVER_PASSWORD"),
                "port": self.context.config.get("REDIS_STORAGE_SERVER_PORT"),
                "sentinel_password": self.context.config.get(
                    "REDIS_SENTINEL_STORAGE_PASSWORD"
                ),
                "socket_timeout": self.context.config.get(
                    "REDIS_SENTINEL_STORAGE_SOCKET_TIMEOUT", 2.0
                ),
                "mode": self.context.config.get(
                    "REDIS_STORAGE_MODE", SINGLE_NODE
                ).lower(),
            },
            "result_storage": {
                "db": self.context.config.get("REDIS_RESULT_STORAGE_SERVER_DB"),
                "host": self.context.config.get("REDIS_RESULT_STORAGE_SERVER_HOST"),
                "instances": self.context.config.get(
                    "REDIS_CLUSTER_RESULT_STORAGE_STARTUP_INSTANCES" if self.context.config.get("REDIS_RESULT_STORAGE_MODE") == CLUSTER else "REDIS_SENTINEL_RESULT_STORAGE_INSTANCES"
                ),
                "master_instance": self.context.config.get(
                    "REDIS_SENTINEL_RESULT_STORAGE_MASTER_INSTANCE"
                ),
                "master_db": self.context.config.get(
                    "REDIS_SENTINEL_RESULT_STORAGE_MASTER_DB", 0
                ),
                "master_password": self.context.config.get(
                    "REDIS_SENTINEL_RESULT_STORAGE_MASTER_PASSWORD"
                ),
                "password": self.context.config.get(
                    "REDIS_RESULT_STORAGE_SERVER_PASSWORD"
                ),
                "port": self.context.config.get("REDIS_RESULT_STORAGE_SERVER_PORT"),
                "sentinel_password": self.context.config.get(
                    "REDIS_SENTINEL_RESULT_STORAGE_PASSWORD"
                ),
                "socket_timeout": self.context.config.get(
                    "REDIS_SENTINEL_RESULT_STORAGE_SOCKET_TIMEOUT", 2.0
                ),
                "mode": self.context.config.get(
                    "REDIS_RESULT_STORAGE_MODE", SINGLE_NODE
                ).lower(),
            },
        }

    def get_storage(self):
        """Get the storage instance.

        :return Redis: Redis instance
        """

        if self.storage:
            return self.storage
        self.storage = self.reconnect_redis()

        return self.storage

    def connect_redis_sentinel(self):
        instances_split = self.storage_values[self.storage_type]["instances"].split(",")
        instances = [tuple(instance.split(":")) for instance in instances_split]

        if self.storage_values[self.storage_type]["sentinel_password"]:
            sentinel_instance = Sentinel(
                instances,
                socket_timeout=self.storage_values[self.storage_type]["socket_timeout"],
                sentinel_kwargs={
                    "password": self.storage_values[self.storage_type][
                        "sentinel_password"
                    ]
                },
            )
        else:
            sentinel_instance = Sentinel(
                instances,
                socket_timeout=self.storage_values[self.storage_type]["socket_timeout"],
            )

        return sentinel_instance.master_for(
            self.storage_values[self.storage_type]["master_instance"],
            socket_timeout=self.storage_values[self.storage_type]["socket_timeout"],
            password=self.storage_values[self.storage_type]["master_password"],
            db=self.storage_values[self.storage_type]["master_db"],
        )

    def connect_redis_single_node(self):
        if self.storage_values[self.storage_type]["password"] is None:
            return Redis(
                port=self.storage_values[self.storage_type]["port"],
                host=self.storage_values[self.storage_type]["host"],
                db=self.storage_values[self.storage_type]["db"],
            )

        return Redis(
            port=self.storage_values[self.storage_type]["port"],
            host=self.storage_values[self.storage_type]["host"],
            db=self.storage_values[self.storage_type]["db"],
            password=self.storage_values[self.storage_type]["password"],
        )

    def connect_redis_cluster(self):
        instances_split = [tuple(instance.strip().split(":")) for instance in self.storage_values[self.storage_type]["instances"].split(",")]
        instances = list(map(lambda x: ClusterNode(x[0], int(x[1] if len(x) == 2 else 6379)), instances_split))

        if self.storage_values[self.storage_type]["password"] is None:
            return RedisCluster(
                startup_nodes=instances,
            )

        return RedisCluster(
            startup_nodes=instances,
            password=self.storage_values[self.storage_type]["password"],
        )

    def reconnect_redis(self):
        shared_client = self.get_shared_storage()
        if shared_client:
            return shared_client

        storage = self.get_storage_redis()
        self.set_shared_storage(storage)

        return storage

    def get_storage_redis(self):
        redis_mode = self.storage_values[self.storage_type]["mode"]
        if redis_mode == SINGLE_NODE:
            return self.connect_redis_single_node()
        if redis_mode == CLUSTER:
            return self.connect_redis_cluster()
        if redis_mode == SENTINEL:
            return self.connect_redis_sentinel()

        if self.storage_type == "storage":
            redis_mode_var = "REDIS_STORAGE_MODE"
        else:
            redis_mode_var = "REDIS_RESULT_STORAGE_MODE"

        raise AttributeError(
            f"Unknown value for {redis_mode_var} {redis_mode}. See README for more information."
        )

    def get_shared_storage(self):
        redis_mode = self.storage_values[self.storage_type]["mode"]

        if not self.shared_client:
            return None

        if redis_mode == SENTINEL and RedisBaseStorage.sentinel_storage:
            return RedisBaseStorage.sentinel_storage

        if redis_mode == SINGLE_NODE and RedisBaseStorage.single_node_storage:
            return RedisBaseStorage.single_node_storage

        if redis_mode == CLUSTER and RedisBaseStorage.cluster_storage:
            return RedisBaseStorage.cluster_storage

        return None

    def set_shared_storage(self, storage):
        redis_mode = self.storage_values[self.storage_type]["mode"]

        if not self.shared_client:
            return None

        if redis_mode == SENTINEL:
            RedisBaseStorage.sentinel_storage = storage

        if redis_mode == SINGLE_NODE:
            RedisBaseStorage.single_node_storage = storage

        if redis_mode == CLUSTER:
            RedisBaseStorage.cluster_storage = storage

        return None
