FROM python:3.10

ARG OPENAI_KEY
ENV OPENAI_KEY=$OPENAI_KEY

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./src /app/

ENV ENVIRONMENT=production

EXPOSE 80

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]