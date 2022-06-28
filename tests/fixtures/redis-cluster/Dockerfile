FROM redis:6-alpine

RUN mkdir -p /redis

WORKDIR /redis

COPY redis-cluster-node-0.conf .
COPY redis-cluster-node-1.conf .
COPY redis-cluster-node-2.conf .

COPY cluster-entrypoint.sh /usr/local/bin/

RUN chown redis:redis /redis/* && \
  chmod +x /usr/local/bin/cluster-entrypoint.sh

EXPOSE 6390
EXPOSE 6391
EXPOSE 6392

ENTRYPOINT ["cluster-entrypoint.sh"]
