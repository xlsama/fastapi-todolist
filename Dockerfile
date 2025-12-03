FROM python:3.14-slim

WORKDIR /app

# 将依赖文件复制到工作目录
COPY pyproject.toml uv.lock ./

# 安装uv
RUN pip install uv
# 安装依赖
RUN uv sync --frozen

# 将所有代码复制到工作目录
COPY . .

# 暴露 FastAPI 默认运行的端口
EXPOSE 8000

# 启动应用
CMD ["uv", "run", "gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info"]
