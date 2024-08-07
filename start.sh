#!/bin/bash
app="hkabtrak"
docker build -t ${app} .
docker run -p 1473:1473 \
  --name=${app} \
  -e SECRET_KEY='your_secret_key_value' \
  -v $PWD/instance:/usr/app/instance ${app}