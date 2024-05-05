#!/usr/bin/env bash

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