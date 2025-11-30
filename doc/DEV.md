# DEV

## 新建项目

```bash 

mkdir crawlEvery
cd crawlEvery/

uv init --python 3.10
uv add Scrapy
. .venv/bin/activate

scrapy startproject GiftInfo ./
```

## 开发

```bash
uv sync
playwright install
```



