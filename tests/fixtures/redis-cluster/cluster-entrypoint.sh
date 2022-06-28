#!/bin/sh

# Cluster nodes
redis-server /redis/redis-cluster-node-0.conf
redis-server /redis/redis-cluster-node-1.conf
redis-server /redis/redis-cluster-node-2.conf

echo yes | redis-cli --cluster create 127.0.0.1:6390 127.0.0.1:6391 127.0.0.1:6392 --cluster-replicas 0

sleep infinity
wait -n
