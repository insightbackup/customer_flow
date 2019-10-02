"""A Pulsar connector to Redis"""
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta

from redis import Redis

from pipeline_utils import SchemaFunction


class RedisConnector(SchemaFunction):
    """a sorted list for each key is stored on redis"""
    def kernel(self, data, context, key_by, value_field, prefix='', group_by=None,
               host='10.0.0.24', port=6379, db=1):
        """Persist data to Redis

        Args:
            data:       dict containing input message data
            context:    Pulsar Context object
            key_by:     The data in this field will be used to determine the key
            value_field:    The data in this field will be stored to Redis
            group_by:   If specified, the results will be saved in a hash instead
                        of as top level key/value pairs in Redis. The value in
                        this field determines the name of the hash
            prefix:     If specified, the hash name will be prefixed by this string
            host:       Redis service URL
            port:       Port for the Redis server
            db:         Redis database index"""
        # Create redis connection
        redis = Redis(host, port=port, db=db)

        # Retrieve the `key` and `value` of the current input
        key = data[key_by] 
        value = data[value_field] 

        # Identify group names and store them to redis
        if group_by:
            if isinstance(str, group_by):
                redis.hset(prefix + data[group_by], key, value)
            else:
                for group in data[group_by]:
                    redis.hset(prefix + group, key, value)
        elif prefix:
            redis.hset(prefix, key, value)
        else:
            redis.set(key, value)

