# API

- [API](#api)
  - [The API](#the-api)
  - [API Url](#api-url)
  - [What aggregate?](#what-aggregate)
  - [Variables - the facts](#variables---the-facts)
  - [Classification and their categories - dimension](#classification-and-their-categories---dimension)
  - [Cities - dimension](#cities---dimension)

## The API

IBGE (Instituto Brasileiro de Geografia e Estatística) is a public institution that provides data about Brazil.

The [API](https://servicodados.ibge.gov.br/api/docs/) provides a lot of information.

Here, the work is concentrated on the [aggregate indicators data](https://servicodados.ibge.gov.br/api/docs/agregados?versao=3#api-bq).

Among availables aggregates, the project focus on inflation data (IPCA - Indice Nacional de Preços ao Consumidor Amplo).

## API Url

The API works with a URL structure like this:

```
https://servicodados.ibge.gov.br/api/v3/
agregados/ { AGGREGATE } /
periodos/ { PERIOD } /
variaveis/63|69|2265|66
?localidades=N7[ { CITY } ]
&classificacao=315[all]
```

For example:

```
https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/202001/variaveis/63|69|2265|66?localidades=N7[1501]&classificacao=315[all]
```


Thus, there are available 3 parameters to retrieve the data:

1. `Aggregate`: The aggregate id. For this project, the aggregate id is `7060`.
2. `Period`: The period of the data. The period is the year and month. For example, `202001`.
3. `City`: The city id. The city id is a number. For example, `1501`.

The other parameters, `variaveis` (variables) and `classificacao` (classification), are fixed.

## What aggregate?

More specifically, the project focus on the inflation data from 2020 onwards. 

In the API, the code for this aggregate is `7060 - IPCA - Variação mensal, acumulada no ano, acumulada em 12 meses e peso mensal, para o índice geral, grupos, subgrupos, itens e subitens de produtos e serviços (a partir de janeiro/2020)`.

Yeah, it's a long name in Portuguese, but it means that the data is about the IPCA index.

## Variables - the facts

For the aggregate, 4 variables are delivered. **Theses variables are the facts of this project**.

There are:
- `63 - IPCA - Variação mensal (%)` : Prices variation by month, that means the inflation rate.
- `69 - IPCA - Variação acumulada no ano (%)`: Accumalate variation within the year.
- `2265 - IPCA - Variação acumulada em 12 meses (%)`: Accumulate variation in 12 running months.
- `66- IPCA - Peso mensal (%)`: The item weight in the calculation.

## Classification and their categories - dimension

Classification stores the categories granularity of the data.

Categories for inflation means the groups of products and services that are used to calculate the inflation index. For example, food, transportation, housing, etc.  
They are divided in levels. House is a level 1 category, and inside it, there are more categories, like rent, electricity, etc.

The main one is `Índice Geral` the only one that has level 0. This represents the aggregate index for all categories.

The avaible categories id and names are also in the API, in the aggregate metadata.

For the project, with `7060` aggregate, the categories data is in:
`'https://servicodados.ibge.gov.br/api/v3/agregados/7060/metadados'`, in the key `classificacao -> categorias`.

## Cities - dimension

The available cities can be retrieved from the API too. 

For the aggregate `7060`, the cities data is in ` 'https://servicodados.ibge.gov.br/api/v3/agregados/7060/localidades/N7'`.

This url returns a list of metropolitan areas of main cities in Brazil where the data is collected.