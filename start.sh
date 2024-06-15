#!/bin/bash
app="hkabtrak"
sudo docker build -t ${app} .
sudo docker run -p 1473:1473 \
  --name=${app} \
  -e SECRET_KEY='your_secret_key_value' \
  -v $PWD/instance:/usr/app/instance ${app}