# Data Engineering 🛠️

- [Data Engineering 🛠️](#data-engineering-️)
  - [Workflow 🔄](#workflow-)
  - [Prodution Tables 📊](#prodution-tables-)
  - [Stage Tables 📊](#stage-tables-)
    - [Raw JSON Data](#raw-json-data)


## Workflow 🔄

The data treatment is performed in the following steps:

For each Airflow `data interval end` period:

- **Dimensional block**
1. `Calendar`: get the year from period and check if it is already in the database.
   1. If not, insert the all the dates for the year in the database.
   2. If yes, do nothing.
2. Retrieve the `categories` from the API.
   1. Check if the category is already in the database.
   2. If not, insert the category in the database.
   3. If yes, update the category name and level.
   4. Insert into the database.
3. Retrieve the `cities` from the API.
   1. Check if the city is already in the database.
   2. If not, insert the city in the database.
   3. If yes, update the city name.
- **Stage block**
1. Retrieve the data for each city to `raw data`.
   1. Check if the period and city data is already in the database.
   2. If not, insert the data in the database.
   3. If yes, update the data in the database.
- **Fact block**
1. Treat the raw data to create the `inflation` fact table.
   1. Explode the JSON data for each city and category.
   2. Get the category id from JSON
   3. Get the inflation value for time serie
   4. Pivot the data to create the fact table with variables as columns.
   5. Delete existing data for the period.
   6. Insert the new data in the database.

## Prodution Tables 📊

Check the [Data Model](Data%20Model.md) for the tables description.

## Stage Tables 📊

The stage tables are the tables that store the raw data from the API.

The data is in an intermediate state, before the fact table creation.

### Raw JSON Data

For each city and time period, data will be retrieved from the API. The most important data is the JSON response, which will be stored in a column for future use.

Table: `raw_data_ibge`

| Columns        | Description                       |
| -------------- | --------------------------------- |
| month_id       | The month of the data             |
| city_id        | The city id                       |
| aggregate_id   | The aggregate id                  |
| aggregate_name | The aggregate name                |
| json_data      | The data in json format           |
| api_url        | The url used to retrieve the data |
| created_at     | The date of the data retrieval    |
| updated_at     | The date of the data update       |