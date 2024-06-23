# Data Engineering Pipeline

- [Data Engineering Pipeline](#data-engineering-pipeline)
  - [Steps](#steps)
    - [Dimension Tables](#dimension-tables)
    - [Raw Table](#raw-table)
    - [Fact Table](#fact-table)

## Steps

### Dimension Tables

The dimension tables are the first information to take from the API.  
This is due to the fact that the id of each city is used in the API url to retrieve data.

1. Cities 
   Read cities from the API and store them in the `cities` table.
2. Categories
   Read categories from the API and store them in the `categories` table.
3. Calendar
   Create a calendar table to store the date information for the project. This could be used in a BI project, for example.
   This is dependent on the year of processing. If the new year is processed, the calendar table will be updated.

### Raw Table

After the dimension tables are created, the raw data is retrieved from the API, based on the cities id from the `cities` table.

For each city id from the `cities` table, the data is retrieved from API and then stored in the `raw_data_ibge` table.

### Fact Table

With the raw data in hand, the fact table can be processed.

The workflow will be consist in:  
    1. Loop for each varible inside JSON  
    2. Get the series value of json  
    3. Put the value in the corresponding variable column  