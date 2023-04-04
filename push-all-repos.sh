#!/bin/bash

# Check if a commit message is provided
if [ -z "$1" ]; then
  echo "Please provide a commit message."
  exit 1
fi

# Set the commit message
commit_message="$1"

# Get the current directory
current_dir=$(pwd)

# Loop through the subdirectories
for dir in "${current_dir}"/*; do
  if [ -d "${dir}" ]; then
    cd "${dir}" || continue
    
    # Check if it's a git repository
    if [ -d .git ]; then
      echo "Performing git operations in $(basename "${dir}")"
      git add -A
      git commit -m "${commit_message}"
      git push
    else
      echo "Skipping $(basename "${dir}"), not a git repository"
    fi

    # Go back to the root folder
    cd "${current_dir}" || exit
  fi
done
