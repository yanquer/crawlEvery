# coding: utf-8

from . import gift_controller
from ..defines import app


@app.get("/")
async def root():
    return {"message": "Hello World"}

