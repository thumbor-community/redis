#!/bin/sh

# Cluster nodes
redis-server /redis/redis-cluster-node-0.conf
redis-server /redis/redis-cluster-node-1.conf
redis-server /redis/redis-cluster-node-2.conf

echo yes | redis-cli --cluster create 127.0.0.1:6390 127.0.0.1:6391 127.0.0.1:6392 --cluster-replicas 0

# wait until cluster_state is ok
while true; do
  echo "$(redis-cli -h localhost -p 6390 CLUSTER INFO 2> /dev/null | grep cluster_state:ok)"
  if [ "$(redis-cli -h localhost -p 6390 CLUSTER INFO 2> /dev/null | grep cluster_state:ok)" != "" ]; then
    break
  fi
  echo .
  sleep 1
done

# wait until cluster_size is 3
while true; do
  echo "$(redis-cli -h localhost -p 6390 CLUSTER INFO 2> /dev/null | grep cluster_size:3)"
  if [ "$(redis-cli -h localhost -p 6390 CLUSTER INFO 2> /dev/null | grep cluster_size:3)" != "" ]; then
    break
  fi
  echo .
  sleep 1
done

# wait until all cluster_slots are ok
# see "RedisCluster specific options" at https://github.com/redis/redis-py
while true; do
  info=$(redis-cli -h localhost -p 6390 CLUSTER INFO 2> /dev/null)
  slots_assigned=$(echo $info | grep "cluster_slots_assigned:" | grep -oE '[0-9]+')
  slots_ok=$(echo $info | grep "cluster_slots_ok:" | grep -oE '[0-9]+')
  if [ "$slots_assigned" == "$slots_ok" ]; then
    break
  fi
  echo .
  sleep 1
done

sleep infinity
wait -n
