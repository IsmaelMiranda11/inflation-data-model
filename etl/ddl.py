'''Definition of tables of the project

This module contains the definition of the tables used in the project.
The tables are defined using the SQLAlchemy ORM.

The target database is PostgreSQL, running in a local Docker container.

'''
from sqlalchemy import Column
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import create_engine, inspect
from sqlalchemy import text

from sqlalchemy.orm import declarative_base

from sqlalchemy.dialects import postgresql

# Define the Base class
Base = declarative_base()

# Define the tables

class cities(Base):
    '''Dimensional Cities table

    The cities are the first information to take from API.
    The id of each city is used in the API url to retrieve data.

    '''

    __tablename__ = 'cities'

    city_id = Column(type_=postgresql.INTEGER, primary_key=True, comment='City id')
    city_name = Column(type_=postgresql.VARCHAR(100), comment='City name')

    created_at = Column(type_=postgresql.TIMESTAMP,
                       server_default=text("(NOW())"),
                       comment='The date of the city insertion')
    updated_at = Column(type_=postgresql.TIMESTAMP,
                       server_default=text("(NOW())"),
                       onupdate=text("(NOW())"),
                       comment='The date of the city update')

class categories(Base):
    '''Categories dimension table

    The categories are retrieved from the metadata.

    '''

    __tablename__ = 'categories'

    category_id = Column(type_=postgresql.INTEGER, primary_key=True,
                         comment='Category id') 
    category_code = Column(type_=postgresql.INTEGER,
                           comment='Category code')
    category_id_name = Column(type_=postgresql.VARCHAR(100),
                             comment='Category id name')
    
    category_name = Column(type_=postgresql.VARCHAR(2000),
                           comment='Category name')
    level = Column(type_=postgresql.INTEGER, comment='Category level')

    created_at = Column(type_=postgresql.TIMESTAMP,
                        server_default=text("(NOW())"),
                        comment='The date of the category insertion')
    updated_at = Column(type_=postgresql.TIMESTAMP,
                        server_default=text("(NOW())"),
                        onupdate=text("(NOW())"),
                        comment='The date of the category update')

class calendar(Base):
    '''Calendar dimension table

    An helper table to be used in data analysis.

    '''

    __tablename__ = 'calendar'

    date = Column(type_=postgresql.DATE, primary_key=True, comment='The date')
    month = Column(type_=postgresql.INTEGER, comment='The month')
    month_name = Column(type_=postgresql.VARCHAR(20), comment='The month name')
    month_abbr = Column(type_=postgresql.VARCHAR(3),
                        comment='The month abbreviation')
    year = Column(type_=postgresql.INTEGER, comment='The year')

class raw_data_ibge(Base):
    '''Raw table to store interval data from API

    This table will be a type I, with an update of row in case of updates.

    '''
    __tablename__ = 'raw_data_ibge'

    month_id = Column(type_=postgresql.INTEGER,
                      comment='The month of the data')
    city_id = Column(type_=postgresql.INTEGER,
                     comment='The city id')
    aggregate_id = Column(type_=postgresql.INTEGER,
                          comment='The aggregate id')
    aggregate_name = Column(type_=postgresql.VARCHAR(100),
                            comment='The aggregate name')
    json_data = Column(type_=postgresql.JSONB,
                       comment='The data in json format')
    api_url = Column(type_=postgresql.VARCHAR(2000),
                     comment='The url used to retrieve the data')

    created_at = Column(type_=postgresql.TIMESTAMP,
                        comment='The date of the data retrieval',
                        server_default=text("(NOW())"))
    updated_at = Column(type_=postgresql.TIMESTAMP,
                        comment='The date of the data update',
                        server_default=text("(NOW())"),
                        onupdate=text("(NOW())"))

    # Define the primary key
    __table_args__ = (
        PrimaryKeyConstraint('month_id', 'city_id'),
    )

    def columns(self):
        return [c.name for c in self.__table__.columns if not c.primary_key] #type:ignore

    def fields_columns(self):
        return [f'"{c}"' for c in self.columns()]


class inflation(Base):
    '''Inflation Fact table

    The fact table will store the data from the API.

    '''

    __tablename__ = 'inflation'

    month_id = Column(type_=postgresql.INTEGER,
                      comment='The month of the data')
    city_id = Column(type_=postgresql.INTEGER,
                     comment='The city id')
    category_id = Column(type_=postgresql.INTEGER,
                         comment='The category id')
    ipca_month_weight = Column(type_=postgresql.NUMERIC,
                               comment='The category weight in the month')
    ipca_month_variation = Column(type_=postgresql.NUMERIC,
                                  comment='Prices variation by month')
    ipca_accumulated_year_variation = Column(type_=postgresql.NUMERIC,
                        comment='Accumalate variation within the year')
    ipca_accumulated_12_months_variation = Column(type_=postgresql.NUMERIC,
                        comment='Accumulate variation in 12 running months')

    # Define the primary key
    __table_args__ = (
        PrimaryKeyConstraint('month_id', 'city_id', 'category_id'),
    )


def create_tables(Base, engine):
    '''Create all tables in Base metadata

    This function will create all tables in the Base metadata.

    First, it will check if the table exists in the database.
    If not, it will create the table.

    '''
    inspector = inspect(engine)

    for table in Base.metadata.tables.values():
        if not inspector.has_table(table.name): #type:ignore
            table.create(engine)


if __name__ == '__main__':

    # Define the engine
    engine = create_engine(
        'postgresql+psycopg2://'
        'postgres:postgres123@'
        'localhost:5432'
    )

    # Create the tables
    create_tables(Base, engine)