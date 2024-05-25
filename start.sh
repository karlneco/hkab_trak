#!/bin/bash
app="hkabtrak"
sudo docker build -t ${app} .
sudo docker run -p 1473:1473 \
  --name=${app} \
  -v $PWD/instance:/usr/app/instance ${app}