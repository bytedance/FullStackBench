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

import asyncio

from openai import AsyncOpenAI
from sandbox_fusion import (
    SubmitRequest,
    TestConfig,
    set_endpoint,
    submit_async,
)
from tqdm.asyncio import tqdm_asyncio
from utils import (
    configurable_retry,
    max_concurrency,
    read_jsonl,
    write_jsonl,
)

set_endpoint('http://localhost:8080')
samples = read_jsonl('./data/fsb_en_20241201.jsonl')
client = AsyncOpenAI(api_key="")


@max_concurrency(50)
@configurable_retry(5)
async def single_inference(prompt: str) -> str:
    completion = await client.chat.completions.create(model="",
                                                      messages=[{
                                                          "role": "user",
                                                          "content": prompt
                                                      }],
                                                      temperature=0.7,
                                                      top_p=0.95)
    return completion.choices[0].message.content


async def process_sample(sample):
    response = await single_inference(sample['content'])
    eval_result = await submit_async(
        SubmitRequest(dataset='FullStackBench',
                      id=sample['id'],
                      completion=response,
                      config=TestConfig(compile_timeout=50,
                                        run_timeout=50,
                                        dataset_type='AutoEvalDataset',
                                        provided_data=sample)))
    return eval_result


async def main():
    results = []
    tasks = [process_sample(sample) for sample in samples]
    for result in await tqdm_asyncio.gather(*tasks):
        results.append(result)
    pass_rate = sum([r.accepted for r in results]) / len(results)
    print(f'pass rate: {pass_rate:.4f}')
    write_jsonl('./results.jsonl', [r.dict() for r in results])


if __name__ == '__main__':
    asyncio.run(main())
