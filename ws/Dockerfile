FROM ubuntu:18.04

RUN apt-get update && apt-get install -y software-properties-common && add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && apt-get install -y python3.6 python3.6-dev python3-pip

RUN ln -sfn /usr/bin/python3.6 /usr/bin/python3 && ln -sfn /usr/bin/python3 /usr/bin/python && ln -sfn /usr/bin/pip3 /usr/bin/pip


RUN apt-get update && \
    apt-get install -y nginx supervisor gunicorn

ENV LANG en_US.UTF-8

WORKDIR /app
COPY . .
RUN pip install pip==21.0.1
RUN pip3 install -r requirements.txt

WORKDIR /app/server
RUN mkdir -p logs

# Setup supervisord
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf


WORKDIR /app
EXPOSE 5555
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 0
ENV PYTHONIOENCODING utf-8
ENV ENV DEV
RUN echo "Australia/Melbourne" > /etc/timezone
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]