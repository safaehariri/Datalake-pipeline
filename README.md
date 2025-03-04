# Datalake-pipeline

## Overview

This project implements an end-to-end data pipeline for processing and analyzing Vélib' bike data in Paris. It automates the tasks of data ingestion, transformation, and indexing using **Apache Airflow**, **Spark**, and **Elasticsearch**, enabling real-time insights into bike availability and station usage. The entire project is containerized using Docker and Docker Compose to ensure easy deployment and portability.

## Technologies Used

- **Apache Airflow**: Task scheduling and workflow orchestration.
- **Apache Spark**: Data processing and transformation.
- **Elasticsearch & Kibana**: Data indexing and visualization.
- **Docker & Docker Compose**: Containerized deployment.
- **Parquet**: Efficient data storage format.

## Project Workflow

1. **Data Ingestion**: Fetches real-time data from the Vélib' API using Apache Airflow.
2. **Data Transformation**: Utilizes Apache Spark to clean, format, and convert JSON data into Parquet format.
3. **Indexing**: Stores the processed data in Elasticsearch for efficient querying and analysis.
4. **Visualization**: Provides insights into bike availability, station usage, and trends via a Kibana dashboard.

## How to Run the Project

To deploy and run the data pipeline, execute the following script:

```bash
./run_containers.sh
