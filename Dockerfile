#Grab the latest alpine image
# Added Labels, change -m to main, expose 8084
# numpy not supported in python 3.12 retrocede to 3.11
# FROM python:3.10.12-alpine3.18
# FROM python:3.12.0a5-alpine3.17
FROM python:3.10.12-slim-bookworm
#FROM python:3.12.0b3-slim-bookworm
LABEL labase.author="carlo@ufrj.br"
LABEL version="23.07-plot"
LABEL description="Alite education platform configured for games - datascience dashboard"
# Install python and pip
# RUN apk add --no-cache --update python3 py-pip bash
ADD ./requirements.txt /tmp/requirements.txt
#RUN apk add --update make cmake gcc g++ gfortran
#RUN apk add --update python3 py-pip python3-dev
#RUN apk --no-cache add musl-dev linux-headers g++
# Install dependencies
RUN python3 -m pip install --upgrade pip
RUN pip install --no-cache-dir -q -r /tmp/requirements.txt
RUN mkdir -p /var/www/alite

# Add local files to the image.
# ADD ./server /var/www/alite/

# Add kwarwp files to the image.
ADD . /var/www/alite

WORKDIR /var/www/alite/src

# Expose is NOT supported by Heroku
EXPOSE 8084

# Run the image as a non-root user
#RUN adduser -D myuser
RUN adduser --system myuser
USER myuser

# ARG port=80

# ENV PORT=$port
# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku
CMD nameko run --config ../nameko.yaml dash.service
# Set-up app folder.

