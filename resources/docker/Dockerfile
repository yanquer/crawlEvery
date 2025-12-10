FROM python:3.12.12-slim-bookworm

WORKDIR /usr/src/app

#COPY requirements.txt ./
#RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install uv
RUN uv sync
RUN . .venv/bin/activate && playwright install

CMD [".venv/bin/python", "main.py"]



