FROM docker.m.daocloud.io/python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置时区为上海，这对股票交易时间很重要
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
# 使用清华源加速下载
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目代码
COPY . .

# 运行主程序
CMD ["python", "main.py"]
