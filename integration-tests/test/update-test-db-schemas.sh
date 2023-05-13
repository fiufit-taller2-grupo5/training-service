#!/bin/bash

cd ../
pwd
docker compose -f ./docker-compose.yml stop postgres-service
docker compose -f ./docker-compose.yml rm -f postgres-service
./update-local-db-schema.sh -f integration-tests/test/docker-test-compose.yml --service user-service
./update-local-db-schema.sh -f integration-tests/test/docker-test-compose.yml --service training-service