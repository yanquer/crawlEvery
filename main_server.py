import asyncio
import logging

logging.basicConfig(level=logging.DEBUG, filename="log/app.log", format="%(asctime)s - %(levelname)s - %(message)s")

import uvicorn

from server import run_server
from server.defines import app

if __name__ == '__main__':
    uvicorn.run(
        app, host="0.0.0.0", port=8091,
        loop="asyncio",
    )
git