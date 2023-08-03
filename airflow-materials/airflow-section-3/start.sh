#!/bin/bash

# Build the base images from which are based the Dockerfiles
# then Startup all the containers at once 
docker build -t hadoop-base docker/hadoop/hadoop-base && \
docker build -t hive-base docker/hive/hive-base && \
docker build -t spark-base docker/spark/spark-base && \
docker-compose up -d --build




# docker build -t hadoop-base docker/hadoop/hadoop-base: This command builds a Docker image named "hadoop-base" using the Dockerfile located in the "docker/hadoop/hadoop-base" directory. This Docker image likely contains the base Hadoop installation.

# docker build -t hive-base docker/hive/hive-base: This command builds a Docker image named "hive-base" using the Dockerfile located in the "docker/hive/hive-base" directory. This Docker image likely contains the base Hive installation.

# docker build -t spark-base docker/spark/spark-base: This command builds a Docker image named "spark-base" using the Dockerfile located in the "docker/spark/spark-base" directory. This Docker image likely contains the base Spark installation.

# docker-compose up -d --build: This command brings up the Docker containers defined in the Docker Compose configuration file and rebuilds the containers if necessary. The -d flag runs the containers in detached mode, meaning they will run in the background. The --build flag ensures that any changes made to the Docker images are applied before starting the containers.