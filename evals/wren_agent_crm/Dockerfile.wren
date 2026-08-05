FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple
COPY core/wren /opt/wren
RUN pip install --no-cache-dir "/opt/wren[mcp]" "mcp>=1.26,<2" "PyMySQL>=1.1,<2"
RUN printf 'import pymysql\npymysql.install_as_MySQLdb()\n' > /usr/local/lib/python3.12/site-packages/sitecustomize.py
WORKDIR /workspace
ENTRYPOINT ["wren"]
