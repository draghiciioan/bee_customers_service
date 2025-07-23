FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install "fastapi>=0.116.1,<0.117.0" \
    "uvicorn>=0.35.0,<0.36.0" \
    "slowapi>=0.1.9,<0.2.0" \
    "pydantic-settings>=2.10.1,<3.0.0" \
    "sqlalchemy>=2.0.41,<3.0.0" \
    "email-validator>=2.2.0,<3.0.0" \
    "aio-pika>=9.5.5,<10.0.0" \
    "python-jose>=3.5.0,<4.0.0" \
    "python-multipart>=0.0.20,<0.0.21" \
    "prometheus-fastapi-instrumentator>=7.1.0,<8.0.0" \
    "asyncpg>=0.30.0,<0.31.0" \
    "redis>=4.0.0,<5.0.0"
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8007"]
