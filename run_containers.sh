#!/bin/bash

# Define colors for better readability
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Step 1: Build Docker Images
echo -e "${GREEN}Building Airflow Docker image...${NC}"
docker build -t my-airflow:2.6.0 -f ./config/Dockerfile.airflow .

echo -e "${GREEN}Building Spark Docker image...${NC}"
docker build -t my-spark-image -f ./config/Dockerfile.spark .

# Check if docker build was successful
if [ $? -ne 0 ]; then
    echo "Failed to build Docker images."
    exit 1
fi

# Step 2: Run Docker Compose
echo -e "${GREEN}Starting containers using Docker Compose...${NC}"
docker-compose up -d

# Check if docker-compose was successful
if [ $? -ne 0 ]; then
    echo "Failed to start containers with Docker Compose."
    exit 1
fi

echo -e "${GREEN}Containers are up and running.${NC}"
