#!/bin/bash
app="hkabtrak"
docker build -t ${app} .
docker run -d -p 1473:1473 \
  --name=${app} \
  -v $PWD:/app ${app}
