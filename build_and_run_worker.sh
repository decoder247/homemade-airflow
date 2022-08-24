#!/bin/bash

docker build \
    -f src/worker/Dockerfile \
    -t hma-worker:latest \
    src &&
    docker run \
        -it --rm \
        --env-file src/worker/variables.env \
        hma-worker:latest
