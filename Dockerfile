#Grab the latest alpine image
# Added Labels, change -m to main, expose 8084
FROM python:3.12.0a5-alpine3.17
LABEL labase.author="carlo@ufrj.br"
LABEL version="23.05"
LABEL description="Alite education platform configured for games"
# Install python and pip
# RUN apk add --no-cache --update python3 py-pip bash
ADD ./requirements.txt /tmp/requirements.txt

# Install dependencies
RUN python3 -m pip install --upgrade pip
RUN pip install --no-cache-dir -q -r /tmp/requirements.txt
RUN mkdir -p /var/www/alite

# Add local files to the image.
# ADD ./server /var/www/alite/

# Add kwarwp files to the image.
ADD . /var/www/alite

WORKDIR /var/www/alite/src/server

# Expose is NOT supported by Heroku
EXPOSE 8084

# Run the image as a non-root user
RUN adduser -D myuser
USER myuser

# ARG port=80

# ENV PORT=$port
# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku
# CMD gunicorn --bind 0.0.0.0:$PORT wsgi
# CMD ["gunicorn"  , "-b", "0.0.0.0:8000", "bottle_app:application"]
CMD python3 -m main
# Set-up app folder.

