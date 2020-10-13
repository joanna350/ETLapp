from sqlalchemy import create_engine
from sqlalchemy.types import Float
from sqlalchemy.types import Integer
from sqlalchemy.types import Text
import pandas as pd
import logging

class Database:
    "Pandas database client"

    def __init__(self, db_uri):
        self.engine = create_engine(
            db_uri,
            echo= True
        )

    def upload_df_to_sql(self, df, table_name):
        '''
        Upload data to db with preformatted dtypes
        :param df: df we want to host on db
        :param table_name: referrable param
        :return: string
        '''
        df.to_sql(table_name,
                  self.engine,
                  if_exists = 'replace',
                  index = False,
                  chunksize = 500,
                  dtype = {
                          "Title": Text,
                          "Year": Integer,
                          "Revenue (Millions GBP)": Float
                          }
                  )

        # usable for logging.debug(mseg)
        mseg = f'INFO: Loading {len(df)} rows INTO {table_name} table'

    def get_df_from_sql(self, table_name):
        '''
        Retrieve dataframe from the SQL table
        :param table_name: referrable param
        :return:
        '''
        table = pd.read_sql_table(
                                  table_name,
                                  con = self.engine
                                  )
        mseg = f'Reloading {len(table)} rows FROM {table_name}'

        # for information - cleaner without logging
        print(table)
        print('\nSummary\n')
        print(table.info())
