#!/bin/bash

IMAGE_TAG=stocktickers
IMAGE_ID=$(docker images -q $IMAGE_TAG)

echo -n "Image ID: $IMAGE_ID"
#docker run -d --network=host --restart on-failure:5 ${IMAGE_ID}
docker run -d --network=host --name stock_crypto_monitor --restart on-failure ${IMAGE_ID}
