FROM ubuntu:18.04

WORKDIR /src

COPY . .

RUN apt update \
    && apt install -y curl \
    && curl -sL https://deb.nodesource.com/setup_14.x  | bash - \
    && apt install -y nodejs \
    && apt install -y python3.8 python3.8-dev python3.8-venv python3.8-distutils \
    && curl https://bootstrap.pypa.io/get-pip.py | python3.8 \
    && cd /usr/local/bin/ \
    && ln -s /usr/bin/python3.8 python

ENV PATH="${PATH}:/src/node_modules/.bin"

RUN cd /src/client && npm install

RUN cd /src/server && pip install -r requirements.txt --ignore-installed

EXPOSE 8000
EXPOSE 3000