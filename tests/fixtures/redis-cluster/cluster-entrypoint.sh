#!/bin/sh

# Cluster nodes
redis-server /redis/redis-cluster-node-0.conf
redis-server /redis/redis-cluster-node-1.conf
redis-server /redis/redis-cluster-node-2.conf

# Join nodes into cluster
echo yes | redis-cli --cluster create 127.0.0.1:6390 127.0.0.1:6391 127.0.0.1:6392 --cluster-replicas 0

# Wait until cluster is up
for port in 6390 6391 6392; do
  echo $port
  while true; do
    cluster_info=$(redis-cli -h localhost -p $port CLUSTER INFO 2> /dev/null)

    cluster_state=$(echo "$cluster_info" | grep "cluster_state:ok" | grep -o 'ok')
    cluster_size=$(echo "$cluster_info" | grep "cluster_size:" | grep -oE '[0-9]+')

    # See "RedisCluster specific options" at https://github.com/redis/redis-py#cluster-mode why we check slots.
    cluster_slots_assigned=$(echo "$cluster_info" | grep "cluster_slots_assigned:" | grep -oE '[0-9]+')
    cluster_slots_ok=$(echo "$cluster_info" | grep "cluster_slots_ok:" | grep -oE '[0-9]+')

    echo "$cluster_state"
    echo "$cluster_size"
    echo "$cluster_slots_assigned"
    echo "$cluster_slots_ok"
    if [ "$cluster_state" == "ok" ] && [ "$cluster_size" == "3" ] && [ "$cluster_slots_assigned" == "$cluster_slots_ok" ]; then
      break
    fi

    echo .
    sleep 1
  done
done

sleep infinity
wait -n
