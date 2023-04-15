#!/bin/bash

REPO_URLS=("git@github.com:fiufit-taller2-grupo5/mobile-app.git" "git@github.com:fiufit-taller2-grupo5/user-service.git" "git@github.com:fiufit-taller2-grupo5/database-schemas.git" "git@github.com:fiufit-taller2-grupo5/web-app.git" "git@github.com:fiufit-taller2-grupo5/training-service.git" "git@github.com:fiufit-taller2-grupo5/development-setup.git" "git@github.com:fiufit-taller2-grupo5/api-gateway.git")
# Get the current directory
CLONE_DIR=$(pwd)

# Change to the target directory
cd "${CLONE_DIR}" || exit
cd ..

# Clone each repository
for repo_url in "${REPO_URLS[@]}"; do
  echo "Cloning ${repo_url}"
  git clone "${repo_url}"
done
