#!/bin/bash

# Get the directory where the script is located
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$PROJECT_DIR"

echo "------------------------------------------"
echo "Starting Auto-Update: $(date)"
echo "Project Directory: $PROJECT_DIR"

# 1. Update version strings in files
# If you need to use a proxy, uncomment and modify the line below:
# export HTTP_PROXY=http://127.0.0.1:7890
python3 update_version.py

if [ $? -ne 0 ]; then
    echo "Error: update_version.py failed. Skipping Docker commands."
    exit 1
fi

# 2. Pull latest images
echo "Pulling latest Docker images..."
docker-compose -p protopie pull

# 3. Update containers
echo "Updating containers..."
docker-compose -p protopie up -d

# 4. Cleanup old images
echo "Cleaning up dangling images..."
docker image prune -f

echo "Update process completed successfully!"
echo "------------------------------------------"
