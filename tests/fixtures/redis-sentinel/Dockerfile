FROM redis:6-alpine

RUN mkdir -p /redis

WORKDIR /redis

COPY redis.conf .
COPY redis-secure.conf .
COPY sentinel.conf .
COPY sentinel-secure.conf .
COPY sentinel-entrypoint.sh /usr/local/bin/

RUN chown redis:redis /redis/* && \
    chmod +x /usr/local/bin/sentinel-entrypoint.sh

EXPOSE 6379
EXPOSE 6380
EXPOSE 26379
EXPOSE 26380

ENTRYPOINT ["sentinel-entrypoint.sh"]
