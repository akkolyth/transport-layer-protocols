#!/bin/bash

init_directories() {
  base_dir="/workspaces/transport-layer-protocols"
  for dir in "$@"; do
    dir_path="$base_dir/$dir"
    if [ -d "$dir_path" ]; then
      python -m mkinit --recursive -w --nomods "$dir_path"
    else
      echo "Error: Directory '$dir_path' does not exist."
    fi
  done
}

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 [directory1] [directory2] [directory3] ..."
  exit 1
fi

init_directories "$@"
