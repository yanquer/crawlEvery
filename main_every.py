import asyncio
import logging
import os.path
import sys

from dotenv import load_dotenv

from common.utils import read_xlsx

load_dotenv()

os.makedirs("log", exist_ok=True)
logging.basicConfig(level=logging.INFO, filename="log/spider.log", format="%(asctime)s - %(levelname)s - %(message)s")
logging.getLogger('scrapy-playwright').setLevel(logging.INFO)


async def main():

    async def _handle_output(stream, stream_name):
        while True:
            line = await stream.readline()
            if not line:
                break
            line = line.decode().strip()
            print(f"[{stream_name}] {line}")

    while True:
        process = await asyncio.create_subprocess_exec(
            '.venv/bin/python',
            'main.py',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=os.environ,
        )
        tasks = [
            asyncio.create_task(_handle_output(process.stdout, 'stdout')),
            asyncio.create_task(_handle_output(process.stderr, 'stderr')),
            ]
        await asyncio.sleep(30 * 60)
        process.kill()
        [x.cancel() for x in tasks]


if __name__ == '__main__':

    print(f'Running in directory: {os.getcwd()}')

    asyncio.run(main())

