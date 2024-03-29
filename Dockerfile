FROM python:3.9-alpine

WORKDIR /opt/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD ["python", "main.py"]
