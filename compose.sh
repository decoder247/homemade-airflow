#!/bin/bash

# # Remove local volumes if error occurs
# docker volume rm xxx-data

# Compose command for running servers
docker-compose \
    --env-file variables_compose.env \
    -f docker-compose.yml down \
    --remove-orphans &&
    docker-compose \
        --env-file variables_compose.env \
        -f docker-compose.yml up \
        --build
# --build   # Compose command for running servers with build flag
