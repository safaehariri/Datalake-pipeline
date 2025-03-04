# Datalake-pipeline

Vélib' Data Pipeline - Big Data Project
Overview

This project implements an end-to-end data pipeline to process and analyze Vélib' bike data in Paris. It automates data ingestion, transformation, and indexing using Apache Airflow, Spark, and Elasticsearch, enabling real-time insights into bike availability and station usage. The project is fully containerized using Docker and Docker Compose for easy deployment and portability.

Technologies Used

Airflow – Task scheduling and workflow orchestration
Spark – Data processing and transformation
Elasticsearch & Kibana – Data indexing and visualization
Docker & Docker Compose – Containerized deployment
Parquet – Efficient data storage format
Project Workflow

Data Ingestion: Fetches real-time data from the Vélib' API using Airflow.
Data Transformation: Uses Spark to clean, format, and convert JSON data into Parquet.
Indexing: Stores processed data in Elasticsearch for efficient querying.
Visualization: A Kibana dashboard provides insights into bike availability, station usage, and trends.
How to Run the Project

To Run the data pipeline, run the script:
./run_containers.sh

Access the services:
Airflow UI: http://localhost:8080
Kibana Dashboard: http://localhost:5601
