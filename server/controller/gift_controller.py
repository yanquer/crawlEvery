# coding: utf-8

from fastapi import FastAPI

from .. import app


@app.get("/gift/{room_id}")
async def root():
    return {"message": "Hello World"}






