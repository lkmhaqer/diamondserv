FROM python:3.8-alpine

RUN mkdir -p /home/app
RUN addgroup -S app && adduser -S app -G app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add --no-cache mariadb-dev \
    && apk add --no-cache \
        supervisor \
        nginx


COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . $APP_HOME
COPY docker/nginx.conf /etc/nginx/nginx.conf

RUN chown -R app:app $HOME
RUN chown -R app:app /var/lib/nginx
USER app

RUN python manage.py collectstatic --noinput

CMD ["supervisord", "--nodaemon", "-c", "/home/app/web/docker/supervisor.conf"]