#Grab the latest alpine image
FROM python:3.12.0a5-alpine3.17
# Install python and pip
# RUN apk add --no-cache --update python3 py-pip bash
ADD ./requirements.txt /tmp/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -q -r /tmp/requirements.txt
RUN mkdir -p /var/www/alite

# Add local files to the image.
# ADD ./server /var/www/igames/

# Add kwarwp files to the image.
ADD . /var/www/alite

WORKDIR /var/www/alite/server

# Expose is NOT supported by Heroku
EXPOSE $PORT

# Run the image as a non-root user
RUN adduser -D myuser
USER myuser

# ARG port=80

# ENV PORT=$port
# Run the app.  CMD is required to run on Heroku
# $PORT is set by Heroku
# CMD gunicorn --bind 0.0.0.0:$PORT wsgi
# CMD ["gunicorn"  , "-b", "0.0.0.0:8000", "bottle_app:application"]
CMD python3 -m tornado_main.py
# Set-up app folder.

