# Arquitetura do projeto

## Airflow
Airflow é executado dentro em um multi-container docker, com webservice e scheduler em separado.

## Postgres

O banco de dados Postgres faz parte do mesmo multicontainer.  
Há dois: um para o airflow e outro com os dados finais de produção. 

## Workflow

### ETL

ETL em python pode ser construído a parte do Airflow.

Deve-se visar a adaptação para o ambiente do Airflow (como conexões e operadores).

O código pode ser desenvolvido na parte de fora do container, com os scripts em pastas fora e conectados ao banco de dados de output. 

### No Airflow

Definitivamente, o código de ETL deve ser feito a parte do Airflow, a fim de organizar os códigos, deixando disponível a documentação para os passos seguidos.  

O foco deve ser entregar funções para serem somente chamadas no Airflow.

## VS Code

Ao fazer um mount dos arquivos no docker, posso editar os arquivos usando o ambiente no docker, que os arquivos no one drive vai ficar 