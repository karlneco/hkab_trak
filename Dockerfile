# Base image
FROM --platform=linux/amd64 python:alpine as build

# Running every next command wih this user
USER root

# Creating work directory in docker
WORKDIR /usr/app

# Copying files to docker
ADD . '/usr/app'

# Installing Flask App
#RUN pip install flask
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Exposing the flask app port from container to host
EXPOSE 1473

RUN chmod u+x /usr/app/entrypoint.sh
ENTRYPOINT ["/usr/app/entrypoint.sh"]

