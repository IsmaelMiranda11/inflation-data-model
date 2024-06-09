# Data Model - IBGE Brazil Inflation 

## Goal 🎯

Creating a data model of IBGE API Brazil inflation data.

## The API Data and Structure 📊

IBGE (Instituto Brasileiro de Geografia e Estatística) is a public institution that provides data about Brazil.

The [API](https://servicodados.ibge.gov.br/api/docs/) provides a lot of information. Here, the work will concentrate on the [aggregate indicators data](https://servicodados.ibge.gov.br/api/docs/agregados?versao=3#api-bq).

Among availables aggregates, the project will focus on inflation data (IPCA - Indice Nacional de Preços ao Consumidor Amplo). 

More specifically, the project will focus on the inflation data from 2020 onwards. In API, the code for this aggregate is `7060 - IPCA - Variação mensal, acumulada no ano, acumulada em 12 meses e peso mensal, para o índice geral, grupos, subgrupos, itens e subitens de produtos e serviços (a partir de janeiro/2020)`.  
Yeah, it's a long name in Portuguese, but it means that the data is about the IPCA index, with monthly variation, accumulated variation within the year, accumulated variation in 12 months, and monthly weight for the general index, groups, subgroups, items, and subitems of products and services.

The API works with a URL structure like this:

```
https://servicodados.ibge.gov.br/api/v3/
agregados/ { AGGREGATE } /
periodos/ { PERIOD } /
variaveis/63|69|2265|66
?localidades=N7[ { CITY } ]
&classificacao=315[all]
```

Thus, there are available 3 parameters to retrieve the data:

1. Aggregate: The aggregate id. For this project, the aggregate id is `7060`.
2. Period: The period of the data. The period is the month and year. For example, `202001`.
3. City: The city id. The city id is a number. For example, `1501`.

The others parameters are fixed: `variaveis` and `classificacao`

The other parameters, `variaveis` (variables) and `classificacao` (classification), are fixed.  

#### Variables

For the aggregate, there's differents variables.

Variables are the interest numbers for this project.

Four will be treated: 
- `63 - IPCA - Variação mensal (%)` : Prices variation by month.
- `69 - IPCA - Variação acumulada no ano (%)`: Accumalate variation within the year.
- `2265 - IPCA - Variação acumulada em 12 meses (%)`: Accumulate variation in 12 running months.
- `66- IPCA - Peso mensal (%)`: The item weight in the calculation.

#### Classification and their categories

Classification stores the categories granularity of the data. 

Categories for inflation means the groups of products and services that are used to calculate the inflation index. For example, food, transportation, housing, etc. They are divided in levels. House is a level 1 category, and inside it, there are more categories, like rent, electricity, etc.

The main one is `Índice Geral` the only one that has level 0. This represents the aggregate index for all categories.

The avaible categories id and names are also in the API, in the aggregate metadata.

For the project, with `7060` aggregate, the categories data is in: 
`'https://servicodados.ibge.gov.br/api/v3/agregados/7060/metadados'`, in the section classificacao -> categorias.


### Cities

The available cities can be retrieved from the API too. For the aggregate `7060`, the cities data is in ` 'https://servicodados.ibge.gov.br/api/v3/agregados/7060/localidades/N7'`.

This url returns a list of metropolitan areas of main cities in Brazil.

## Data Treatment  🛠️

### Workflow 🔄

The data treatment will be done in the following steps:

For each Airflow data interval period:
1. Retrieve the cities from the API.
   1. Check if the city is already in the database.
   2. If not, insert the city in the database.
   3. If yes, update the city name.
2. Retrieve the categories from the API.
   1. Check if the category is already in the database.
   2. If not, insert the category in the database.
   3. If yes, update the category name and level
3. Retrieve the data for each city
   1. Check if the period and city data is already in the database.
   2. If not, insert the data in the database.
   3. If yes, update the data in the database.
4. Treat the raw data to create the fact table.

### Dimensional Tables 📊

#### Cities 🏙️

The cities are the first information to take from API. The id of each city is used in the API url to retrieve data.

Table: `cities`
| Colunm | Description |
| --- | --- |
| id | City id |
| name | City name |

#### Categories 📚

The categories are retrieved from the metadata.

Table: `categories`

Columns | Description
--- | ---
id | Category id
id_name | Category name with id
name | Category name
level | Category level

#### Calendar 📅

A calendar table will be created to store the date information for the project. This could be used in a BI project, for example.

However, it is important to note that the data is retrieved by month. So that, the principal Calendar table use is for monthly data.

Table: `calendar`

Columns | Description
--- | ---
date | The date
month | The month
year | The year
quarter | The quarter
### Raw Tables 📊

#### Raw JSON Data

For each city and time period, data will be retrieved from the API. The most important data is the JSON response, which will be stored in a column for future use.

Table: `raw_data_ibge`

Columns | Description
--- | ---
month_id | The month of the data
city_id | The city id
aggregate_id | The aggregate id
aggregate_name | The aggregate name
json_data | The data in json format
api_url | The url used to retrieve the data
created_at | The date of the data retrieval
updated_at | The date of the data update

### Fact Table 

#### Inflation 📈

The fact table will store the data from the API.

Table: `inflation`

Columns | Description
--- | ---
month_id | The month of the data
city_id | The city id
category_id | The category id
ipca_month_weight | The category weight in the month
ipca_month_variation_% | Prices variation by month
ipca_accumulated_year_variation_% | Accumalate variation within the year
ipca_accumulated_12_months_variation_% | Accumulate variation in 12 running months

