# Project Architecture

- [Project Architecture](#project-architecture)
  - [Docker](#docker)
    - [Airflow](#airflow)
    - [PostgreSQL](#postgresql)
  - [Python](#python)

## Docker

Docker is used to containerize the project.

The `compose.yaml` file is used to define the services and the network of the project.

Basically, the project has two services: `data-postgres` and `airflow`.

The `data-postgres` service is the PostgreSQL database. It is used to store the data.

The `airflow` service is the Apache Airflow service. It is used to orchestrate the data pipeline.

Some files are sincronized with the services, like the `dags` and `etl` folders.

### Airflow 

An `entrypoint script` is used to start the Airflow service, with these steps:
- Install the required Python packages
- Create project tables in the database
- Initialize the Airflow database
- Create the user admin
- Create the connection to the PostgreSQL database
- Serialize the DAGs
- Make the dag unpaused
- Start the Airflow service

There is also an env file to set some Airflow environment variables.

The service is open at port `8980` with user `admin` and password `admin`.

### PostgreSQL

The PostgreSQL service is open at port `5432` with user `postgres` and password `postgres123`.

A volume is used to persist the data in the database. That means that the data is not lost when the container is stopped, only when it is removed.

## Python

Python is used as the main programming language of the project.

The `create_tables.py` script is used to create the tables in the database.  
The `etl` folder contains the scripts to extract, transform and load the data.  
The `dags` folder contains the Airflow DAGs to orchestrate the ETL process.  

These are the main Python libraries used in the project:
- `pandas` to manipulate the data
- `sqlalchemy` to connect to the database
- `requests` to get the data from the API
- `apache-airflow` to orchestrate the ETL process