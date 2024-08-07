#!/bin/bash
app="hkabtrak"
docker build -t ${app} .
docker run -p 1473:1473 \
  --name=${app} \
  --env-file ~/hkab_trak.env \
  -v hkabtrak_migrations:/app/migrations \
  -v $PWD/instance:/app/instance \
  -v $PWD:/app ${app}