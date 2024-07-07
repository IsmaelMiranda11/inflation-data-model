# Data Model

![erd](docs/erd.png)

- [Data Model](#data-model)
    - [Dimensional Tables 📊](#dimensional-tables-)
      - [Calendar 📅](#calendar-)
      - [Cities 🏙️](#cities-️)
      - [Categories 📚](#categories-)
    - [Fact Table](#fact-table)
      - [Inflation 📈](#inflation-)


### Dimensional Tables 📊

#### Calendar 📅

The calendar table is the date dimension table of the project.

For each processed year, all dates of the year are available in the table.

However, it is important to note that the data is retrieved by month. So that, the principal Calendar table use is for monthly data.

Table: `calendar`

| Column     | Description            |
| ---------- | ---------------------- |
| date       | The date               |
| month      | The month              |
| month_name | The month name         |
| month_abbr | The month abbreviation |
| year       | The year               |

#### Cities 🏙️

The cities are the first information to take from API. 

The id of each city is used in the API url to retrieve data.

For visualization purposes, the city name could be used.

Table: `cities`

| Colunm     | Description                    |
| ---------- | ------------------------------ |
| city_id    | City id                        |
| city_name  | City name                      |
| cretead_at | The date of the city insertion |
| updated_at | The date of the city update    |

#### Categories 📚

The categories are retrieved from the API metadata.

The data is retrieved in format `<category_code>.<category_name>`. A small treament is performed and the code and name are available in the table.

**Take care with the level column.** The data should always be analyzed by level, just because inflation is a rate and loses its meaning if the number are not aggregated correctly.

Table: `categories`

| Column           | Description                        |
| ---------------- | ---------------------------------- |
| category_id      | Category id                        |
| category_code    | Category code                      |
| category_id_name | Category name with id              |
| category_name    | Category name                      |
| level            | Category level                     |
| created_at       | The date of the category insertion |
| updated_at       | The date of the category update    |

### Fact Table

#### Inflation 📈

The inflation table is the fact table of the project.

**None of the fact columns are additive!**

The data should be slieced by city, category level, category and date.

Table: `inflation`

| Column                               | Description                               |
| ------------------------------------ | ----------------------------------------- |
| month_id                             | The month of the data                     |
| month_date                           | The date of the month                     |
| city_id                              | The city id                               |
| category_id                          | The category id                           |
| ipca_month_weight                    | The category weight in the month          |
| ipca_month_variation                 | Prices variation by month                 |
| ipca_accumulated_year_variation      | Accumalate variation within the year      |
| ipca_accumulated_12_months_variation | Accumulate variation in 12 running months |

