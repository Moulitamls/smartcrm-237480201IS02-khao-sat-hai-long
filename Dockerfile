FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1

# 1. Tệp khoá trước: chỉ cài lại thư viện khi requirements.txt đổi (tận dụng cache)
COPY requirements.txt .
RUN pip install -r requirements.txt

# 2. Mã nguồn (gồm cả test, để chạy pytest trong container) và CSV nguồn
COPY src ./src
COPY data/raw ./data/raw
COPY start.sh ./start.sh

RUN useradd -m appuser && mkdir -p /var/lib/csat && chown -R appuser /app /var/lib/csat
USER appuser

EXPOSE 8501
CMD ["sh", "start.sh"]
