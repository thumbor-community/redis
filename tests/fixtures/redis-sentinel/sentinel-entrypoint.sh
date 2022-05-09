#!/bin/sh

# Master
redis-server /redis/redis.conf
redis-server /redis/redis-secure.conf

# Sentinel
redis-server /redis/sentinel.conf --sentinel
redis-server /redis/sentinel-secure.conf --sentinel

sleep infinity
wait -n
