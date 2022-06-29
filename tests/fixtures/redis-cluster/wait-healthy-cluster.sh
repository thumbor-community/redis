#!/bin/sh

# Wait until cluster is up
while true; do
  cluster_info=$(redis-cli -h localhost -p 6390 CLUSTER INFO 2> /dev/null)

  cluster_state=$(echo "$cluster_info" | grep "cluster_state:ok" | grep -o 'ok')
  cluster_size=$(echo "$cluster_info" | grep "cluster_size:" | grep -oE '[0-9]+')

  # See "RedisCluster specific options" at https://github.com/redis/redis-py#cluster-mode why we check slots.
  cluster_slots_assigned=$(echo "$cluster_info" | grep "cluster_slots_assigned:" | grep -oE '[0-9]+')
  cluster_slots_ok=$(echo "$cluster_info" | grep "cluster_slots_ok:" | grep -oE '[0-9]+')

  if [ "$cluster_state" == "ok" ] && [ "$cluster_size" == "3" ] && [ "$cluster_slots_assigned" == "$cluster_slots_ok" ]; then
    break
  fi

  echo .
  sleep 1
done
