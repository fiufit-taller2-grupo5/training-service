FROM python:3.10

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./src /app/

ENV ENVIRONMENT=production

CMD ["uvicorn", "server:app", "--port", "80"]