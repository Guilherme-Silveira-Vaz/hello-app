FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ARG APP_VERSION=unknown
ENV APP_VERSION=${APP_VERSION}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"] 
