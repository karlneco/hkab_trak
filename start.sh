#!/bin/bash
app="hkabtrak"
docker build -t ${app} .
docker run -d -p 10400:80 \
  --name=${app} \
  -v $PWD:/app ${app}
