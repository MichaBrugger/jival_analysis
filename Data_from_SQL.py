import os
import glob
import pyodbc
import pandas as pd

class get_Data:

    # To establish this connection:
    # 1. Download and install ODBC Driver 17
    # 2. Add connection in ODBC-Datasource Manager with following SQL Sever authentification credentials: Server: 182.18.139.135, UID: jvl_readonly, PW:jvl@@1

    Conn_SQL = pyodbc.connect('DSN=Jivana_Vitality; UID=jvl_readonly; PWD=jvl@@1;Trusted_Connection=no')  # establishing connection with the pyodbc library

    def __init__(self, SQL_Folder, Queries, date):

        self.SQL_Folder = SQL_Folder
        self.Queries = Queries
        self.date = date

    # While working in India we often had the problem that our internet would just stop working for a few hours
    # so I decided to store the content of the queries locally, so if I was able to access the data at least
    # once a day, I was still able work with the data for the rest of that day. In addition to this it made re-
    # peated runs of the code faster.

    # At the same time I had to make sure that I don't use old data accidentally. So I wrote the code in a way
    # that it always deletes old files of the same file path/name but with a different date/ending. Also other
    # files with totally different names are left untouched, in case someone stores something different in the
    # folder.


    def get_data_from_sql(self):
        if not os.path.exists(self.SQL_Folder):
            os.makedirs(self.SQL_Folder)
        for Query_Name, Query in self.Queries.items():
            global csv_name
            csv_name = '{}_'.format(Query_Name) + self.date + '.csv'
            if not os.path.exists(self.SQL_Folder + csv_name):
                for filename in glob.glob("{0}{1}_*".format(self.SQL_Folder, Query_Name)):
                    try:
                        os.remove(filename)
                        print('{} removed'.format(filename))
                    except:
                        print('Remove {} is not possible'.format(Query_Name))
                pd.read_sql_query(Query, self.Conn_SQL).to_csv(self.SQL_Folder + csv_name)
                print('{} downloaded successful'.format(Query_Name))
            else:
                print('{} already downloaded'.format(Query_Name))

    # store_csv_to_df function to take csv into dataframe
    def store_csv_to_df(self):

        # Read data from file 'SQL_Trip_2018-12-16.csv'
        # (in the same directory that your python process is based)
        # Control delimiters, rows, column names with read_csv (see later)
        DF_Trip = pd.read_csv(self.SQL_Folder + "SQL_Trip_{}.csv".format(self.date))
        DF_TripHeader = pd.read_csv(self.SQL_Folder + "SQL_TripHeader_{}.csv".format(self.date))
        dataframes = [DF_Trip, DF_TripHeader]
        print('Dataframes stored')
        return dataframes