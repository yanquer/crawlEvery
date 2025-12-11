FROM mcr.microsoft.com/playwright:v1.57.0-noble

# 安装 Python 3, pip 及基本工具
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv && \
    # 创建软链接，将 python 指向 python3
    ln -s /usr/bin/python3 /usr/local/bin/python && \
    # 清理缓存以减小镜像体积
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 验证安装（可选，调试用）
RUN python --version && pip --version


WORKDIR /usr/src/app

#COPY requirements.txt ./
#RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -m venv .venv
RUN . .venv/bin/activate && pip install uv
RUN #. .venv/bin/activate && uv sync
RUN . .venv/bin/activate && UV_PYTHON_INSTALL_MIRROR=https://mirror.nju.edu.cn/github-release/indygreg/python-build-standalone/ uv sync
RUN . .venv/bin/activate && playwright install

CMD [".venv/bin/python", "main_server.py"]



