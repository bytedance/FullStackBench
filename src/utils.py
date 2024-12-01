# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import asyncio
import json
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

logger = logging.getLogger(__name__)


def on_retry_error(s):
    e = s.outcome.exception()
    logger.error(f'give up retrying. error: {e}')
    raise e


def before_retry_sleep(s):
    msg = f'function call error for {s.attempt_number} time(s), will retry... error: {s.outcome.exception()}'
    if s.attempt_number > 2:
        logger.warning(msg)
    else:
        logger.debug(msg)


def configurable_retry(max_attempts):

    def decorator(func):

        @wraps(func)
        @retry(wait=wait_exponential_jitter(),
               stop=stop_after_attempt(max_attempts),
               before_sleep=before_retry_sleep,
               retry_error_callback=on_retry_error)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        @wraps(func)
        @retry(wait=wait_exponential_jitter(),
               stop=stop_after_attempt(max_attempts),
               before_sleep=before_retry_sleep,
               retry_error_callback=on_retry_error)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def read_jsonl(fn):
    with open(fn) as f:
        return [json.loads(l) for l in f.readlines()]


def write_jsonl(fn, data):
    with open(fn, 'w') as f:
        f.write('\n'.join([json.dumps(l, ensure_ascii=False) for l in data]))


def max_concurrency(limit: int):
    """ Decorator to limit the maximum number of concurrent executions of an async function """
    semaphore = asyncio.Semaphore(limit)

    def decorator(func):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with semaphore:
                return await func(*args, **kwargs)

        return wrapper

    return decorator
