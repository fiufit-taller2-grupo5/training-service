#!/bin/bash

# Step 1: Execute docker compose up for running the db
docker compose up -d

# Step 2: Wait for the database to be ready
container_name="postgres-service"  # Replace with the name of your PostgreSQL container
db_host="localhost"
db_port="5432"
db_user="postgres"
db_password="12345678"
db_name="postgres"

echo "Waiting for database to be ready..."
while ! docker exec -e PGPASSWORD="$db_password" -it "$container_name" psql -h "$db_host" -p "$db_port" -U "$db_user" -w -d "$db_name" -c "SELECT 1" > /dev/null 2>&1; do
  sleep 1
done
echo "Database is ready."

# Step 2: Create/overwrite .env file
PRISMA_ENV_PATH="../user-service/database/prisma/prisma/.env"
mkdir -p "$(dirname "$PRISMA_ENV_PATH")"
echo "DATABASE_URL=postgresql://postgres:12345678@localhost:5432/postgres?schema=public" > "$PRISMA_ENV_PATH"

# Step 3: Execute yarn and npx prisma db push
cd ../user-service/database/prisma
yarn && npx prisma db push

# Step 4: Stop the database
cd ../../../development-setup
docker compose down
echo "Database stopped. Update successful."