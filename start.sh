#!/bin/bash
app="hkabtrak"
sudo docker build -t ${app} .
sudo docker run -d -p 1473:1473 \
  --name=${app} \
  -v $PWD:/app ${app}
