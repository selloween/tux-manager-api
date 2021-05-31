#https://github.com/tiangolo/uwsgi-nginx-flask-docker
FROM tiangolo/uwsgi-nginx-flask
ENV LISTEN_PORT 8080
EXPOSE 8080
#ENV STATIC_URL /static
#ENV STATIC_PATH /app/app/static
RUN apt-get update -y
RUN apt-get install -y libmariadb3 libmariadb-dev
COPY ./app/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt