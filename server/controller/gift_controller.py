# coding: utf-8

from fastapi import FastAPI

from ..defines import app


@app.get("/gift/{room_id}")
async def root():
    return {"message": "Hello World"}






