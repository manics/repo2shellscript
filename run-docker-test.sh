#!/bin/bash
set -eux

IMAGE_NAME=test-repo2shellscript

repo2docker --engine shellscript --user-id 1000 --user-name test --no-run --image-name $IMAGE_NAME https://github.com/binder-examples/conda

# Test by building a Docker image with packer
cd ./repo2shellscript-output/$IMAGE_NAME
packer build repo2docker.pkr.hcl

docker run -d --name test -p 8888:8888 $IMAGE_NAME
sleep 5

# If container is slow to start the reply may be empty, so retry
URL=http://127.0.0.1:8888/api
i=0
while ! curl --fail $URL; do
    i=$(($i+1))
    if [ $i -ge 5 ]; then
        echo "$(date) - $URL failed, giving up"
        echo "docker logs:"
        docker logs test
        exit 1
    fi
    echo "$(date) - $URL failed, retrying ..."
    sleep 5
done
