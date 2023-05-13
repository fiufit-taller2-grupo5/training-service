#!/bin/bash

# make sure yarn is available
if ! command -v yarn &> /dev/null
then
    echo "yarn could not be found"
    exit
fi

# update test db schemas
chmod +x ./test/update-test-db-schemas.sh
./test/update-test-db-schemas.sh

# check command line argument to determine which test to run
if [ "$1" == "user" ]; then
    yarn test:user
elif [ "$1" == "training" ]; then
    yarn test:training
else
    echo "Invalid argument. Please use 'user' or 'training'"
fi

