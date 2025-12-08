# coding: utf-8


. .venv/bin/activate
uvicorn server.run_server:app --host 0.0.0.0 --port 8091    # --reload

