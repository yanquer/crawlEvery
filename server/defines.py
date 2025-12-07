# coding: utf-8
from pathlib import Path

from fastapi import FastAPI

app = FastAPI()


PROJECT_ROOT = Path(__file__).parent.parent
print(f'project dir: {PROJECT_ROOT}')



