#!/bin/bash

# Get the current directory
current_dir=$(pwd)

# Loop through the subdirectories
for dir in "${current_dir}"/*; do
  if [ -d "${dir}" ]; then
    cd "${dir}" || continue
    
    # Check if it's a git repository
    if [ -d .git ]; then
      echo "Pulling in $(basename "${dir}")"
      git pull
    else
      echo "Skipping $(basename "${dir}"), not a git repository"
    fi

    # Go back to the root folder
    cd "${current_dir}" || exit
  fi
done
