#!/bin/bash

# Get the current directory
current_dir=$(pwd)

# Loop through the subdirectories
for dir in "${current_dir}"/*; do
  if [ -d "${dir}" ]; then
    cd "${dir}" || continue
    
    # Check if it's a git repository
    if [ -d .git ]; then
      # Get the SSH URL for the Git repository
      git_ssh_url=$(git config --get remote.origin.url | sed 's/https:\/\/github\.com/git@github.com:/')

      if [ -n "${git_ssh_url}" ]; then
        echo "Pulling in $(basename "${dir}")"
        git pull "${git_ssh_url}"
      else
        echo "Skipping $(basename "${dir}"), no SSH URL found"
      fi
    else
      echo "Skipping $(basename "${dir}"), not a git repository"
    fi

    # Go back to the root folder
    cd "${current_dir}" || exit
  fi
done

