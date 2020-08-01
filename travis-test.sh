#!/bin/bash
set -eux

repo2docker --engine shellscript --user-id 1000 --user-name test --no-run --image-name test-repo2shellscript https://github.com/binder-examples/conda

# Test by spinning up a plain ubuntu:18.04 VM and executing the scripts
docker run -d --name test -p 8888:8888 -v $PWD/repo2shellscript-output/test-repo2shellscript:/src:ro ubuntu:18.04 sleep 1h
docker exec test /src/repo2shellscript-build.bash
docker exec test sudo -iu test /src/repo2shellscript-start.bash &
sleep 5

# URL=$(docker logs repo2shellscript | grep 'http://127.0.0.1:8888/?token=' | tail -n1 | awk '{print $2}')

curl -f http://127.0.0.1:8888/api
