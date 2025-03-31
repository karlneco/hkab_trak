#!/bin/bash
app="hkabtrak"

docker build -t ${app} .

docker run -p 80:80 -p 1473:1473 \
  --name=${app} \
  --env-file ~/hkab_trak.env \
  -e DOMAIN=absent.calgaryhoshuko.org \
  -e EMAIL=it@calgaryhoshuko.org \
  -v $PWD/migrations:/app/migrations \
  -v $PWD/instance:/app/instance \
  -v letsencrypt:/etc/letsencrypt \
  -v letsencrypt-lib:/var/lib/letsencrypt \
  ${app}