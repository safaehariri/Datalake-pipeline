#!/bin/bash
# Attendre que PostgreSQL soit prêt
until pg_isready -h postgres -U airflow; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 1
done

# Initialiser la base de données si nécessaire
if [ ! -f "/opt/airflow/initialized" ]; then
    airflow db init

    airflow db upgrade

    # Créer l'utilisateur admin si non existant
    if ! airflow users list | grep -q admin; then
        airflow users create \
          --username admin \
          --firstname Safae \
          --lastname Hariri \
          --role Admin \
          --email safae045@gmail.com \
          --password admin
    fi

    # Créer la connexion API

    airflow connections add 'velib_api_connection' \
        --conn-type 'http' \
        --conn-host 'https://velib-metropole-opendata.smovengo.cloud/opendata/Velib_Metropole/'

    # Update the PostgreSQL connection with the correct credentials
    airflow connections delete 'postgres_default' || true
    airflow connections add 'postgres_default' \
        --conn-type 'postgres' \
        --conn-host 'postgres' \
        --conn-schema 'airflow' \
        --conn-login 'airflow' \
        --conn-password 'airflow' \
        --conn-port 5432

    airflow connections delete 'spark_default' || true
    airflow connections add 'spark_default' \
        --conn-type 'spark' \
        --conn-host 'spark-master' \
        --conn-port 7077



    touch /opt/airflow/initialized
fi

# Lancer le webserver Airflow
exec airflow webserver

