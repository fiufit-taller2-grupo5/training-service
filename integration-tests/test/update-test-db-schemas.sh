#!/bin/bash

cd ../
pwd
./update-local-db-schema.sh -f integration-tests/test/docker-test-compose.yml --service user-service
./update-local-db-schema.sh -f integration-tests/test/docker-test-compose.yml --service training-service


