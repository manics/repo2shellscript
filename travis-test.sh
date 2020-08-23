#!/bin/bash
set -eux

pytest -v tests/

IMAGE_NAME=test-repo2shellscript

repo2docker --engine shellscript --user-id 1000 --user-name test --no-run --image-name $IMAGE_NAME https://github.com/binder-examples/conda

# Test by building a Docker image with packer
cd ./repo2shellscript-output/$IMAGE_NAME
packer build repo2docker.pkr.hcl

docker run -d --name test -p 8888:8888 $IMAGE_NAME
sleep 5

# URL=$(docker logs repo2shellscript | grep 'http://127.0.0.1:8888/?token=' | tail -n1 | awk '{print $2}')

curl -f http://127.0.0.1:8888/api
