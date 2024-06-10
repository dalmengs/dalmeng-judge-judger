#!/bin/bash

touch .env
declare -a env_vars=(
  "JUDGE_SERVER_PORT"
  "LOG_DIRECTORY"
  "CHUNK_SIZE"
  "DEFAULT_TIME_LIMIT"
  "DEFAULT_MEMORY_LIMIT"
)

for var_name in "${env_vars[@]}"; do
    if [ ! -z ${!var_name+x} ]; then
        echo "$var_name=${!var_name}" >> .env
    fi
done

python3 Main.py
