#!/bin/bash

docker build \
    -f src/orchestrator/Dockerfile \
    -t hma-orchestrator:latest \
    src &&
    docker run \
        -it --rm \
        --env-file src/orchestrator/variables.env \
        hma-orchestrator:latest
