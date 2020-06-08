FROM ubuntu:18.04

MAINTAINER Trevor Liberty "tliberty@pdx.edu"

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD exec gunicorn --bind :${PORT:-80} --workers 1 --threads 8 app:app
