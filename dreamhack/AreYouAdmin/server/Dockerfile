FROM python:3.10-slim-bookworm

ENV PORT 8000

RUN apt-get update -y && apt-get install -y python3-pip build-essential wget curl unzip

## chrome


## chromedriver
RUN wget https://storage.googleapis.com/chrome-for-testing-public/`curl -sS https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE`/linux64/chromedriver-linux64.zip \
    && unzip chromedriver-linux64.zip \
    && rm chromedriver-linux64.zip

WORKDIR /app

COPY ./deploy/app /app

RUN pip install -r requirements.txt
RUN chmod +x run.sh

EXPOSE $PORT

CMD ["./run.sh"]