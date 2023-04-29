#!/bin/bash

# Step 1: Start the databases
sudo docker-compose up -d 
# Step 2: Wait for the databases to be ready
container_name_testing="postgres-test-service"
db_host_testing="localhost"
db_port_testing="5435"
db_user_testing="postgres-test"
db_password_testing="12345678"
db_name_testing="postgres_test"

echo "Waiting for testing database to be ready..."
while ! sudo docker exec -e PGPASSWORD="$db_password_testing" -it "$container_name_testing" psql -h "$db_host_testing" -p "$db_port_testing" -U "$db_user_testing" -w -d "$db_name_testing" -c "SELECT 1" > /dev/null 2>&1; do
  sleep 1
done
echo "Testing database is ready."

# Step 3: Create/overwrite .env files
PRISMA_ENV_PATH_TESTING="./integration-tests/database/prisma/prisma/.env"
mkdir -p "$(dirname "$PRISMA_ENV_PATH_TESTING")"
echo "DATABASE_URL=postgresql://${db_user_testing}:${db_password_testing}@${db_host_testing}:${db_port_testing}/${db_name_testing}?schema=user-service" > "$PRISMA_ENV_PATH_TESTING"

# Step 4: Execute yarn and npx prisma db push for both databases
cd ./integration-tests/database/prisma
yarn && npx prisma db push --preview-feature

# Step 5: Stop the databases
cd ../../..
sudo docker-compose down
echo "Databases stopped. Update successful."
