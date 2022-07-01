#!/bin/sh

cat ./tests/fixtures/redis-cluster/wait-healthy-cluster.sh | docker exec $(docker ps | grep redis-cluster | grep -oE "^[0-9a-z]+") /bin/sh
