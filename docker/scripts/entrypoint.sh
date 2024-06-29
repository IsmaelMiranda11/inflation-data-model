#!/usr/bin/env bash

# Airflow setup
airflow db migrate

airflow users create \
    --username admin \
    --password admin \
    --firstname Airflow \
    --lastname Admin \
    --role Admin \
    --email admin@any.com

airflow connections add \
    postgres_default \
    --conn-description "Postgress database connection" \
    --conn-port 5432 \
    --conn-type postgres \
    --conn-host host.docker.internal \
    --conn-schema postgres \
    --conn-login postgres \
    --conn-password postgres123

airflow standalone

# Process the dag
airflow dags reserialize

# Unpause the dag dimensional_model_ibge
airflow dags unpause dimensional_model_ibge

# Install requirements
pip install -r requirements.txt

# Create tables in database
python /opt/airflow/etl/create_tables.py

