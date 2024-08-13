#!/bin/bash

autoflake_directory() {
  base_directory="/workspaces/python-template/"
  directory="$1"
  full_directory="${base_directory}${directory}"
  if [ -d "$full_directory" ]; then
    find "$full_directory" -type f -name "*.py" -exec autoflake --in-place --remove-all-unused-imports {} \;
  else
    echo "Error: Directory '$full_directory' does not exist."
  fi
}

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 [directory1] [directory2] [directory3] ..."
  exit 1
fi

for dir in "$@"; do
  autoflake_directory "$dir"
done
