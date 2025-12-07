# coding: utf-8
from server.controller.gift_controller import GiftController
from server.defines import app
from server import controller

def run_server():
    ...
    controller = GiftController()


run_server()

# if __name__ == '__main__':
#     run_server()

# uvicorn.run(app, host="0.0.0.0", port=8000)
