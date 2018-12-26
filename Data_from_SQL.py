import os
import glob
import pyodbc
import pandas as pd

"""
While working in India we often had the problem that our internet would just stop working for a few hours so
I decided to store the content of the queries locally, so if I was able to access the data at least once a day,
I was still able work with the data for the rest of that day. In addition to this it made repeated runs of the code faster.

At the same time I had to make sure that I don't use old data accidentally. So I wrote the code in a way
that it always deletes old files of the same file path/name but with a different date/ending. Also other
files with totally different names are left untouched, in case someone stores something different in the folder.
"""

class get_Data:

    """
    To establish this connection:
    1. Download and install ODBC Driver 17
    2. Add connection in ODBC Data Source Administrator (Windows) with following SQL Server authentification credentials:
    Connection Name: Jivana_Vitality, Server: 182.18.139.135, UID: jvl_readonly, PW:jvl@@1
    """

    # establishing connection through the pyodbc library
    Conn_SQL = pyodbc.connect('DSN=Jivana_Vitality; UID=jvl_readonly; PWD=jvl@@1;Trusted_Connection=no')

    def __init__(self, SQL_Folder, Queries, date):

        self.SQL_Folder = SQL_Folder
        self.Queries = Queries
        self.date = date

    def get_data_from_sql(self):

        # Creating folders if they don't exist, pulling the data from SQL and store it as csv
        if not os.path.exists(self.SQL_Folder):
            os.makedirs(self.SQL_Folder)
        for Query_Name, Query in self.Queries.items():
            csv_name = '{}_'.format(Query_Name) + self.date + '.csv'
            if not os.path.exists(self.SQL_Folder + csv_name):
                for filename in glob.glob("{0}{1}_*".format(self.SQL_Folder, Query_Name)):
                    try:
                        os.remove(filename)
                        print('{} removed'.format(filename))
                    except:
                        print('Remove {} is not possible'.format(Query_Name))
                pd.read_sql_query(Query, self.Conn_SQL).to_csv(self.SQL_Folder + csv_name, index=False)
                print('{} downloaded successful'.format(Query_Name))
            else:
                print('{} already downloaded'.format(Query_Name))

    def store_csv_to_df(self):

        # Reading data from different csv files to df and make them accessible for Main_Analysis
        DF_Trip = pd.read_csv(self.SQL_Folder + "SQL_Trip_{}.csv".format(self.date))
        DF_TripHeader = pd.read_csv(self.SQL_Folder + "SQL_TripHeader_{}.csv".format(self.date))
        DF_CustomerAccounts = pd.read_csv(self.SQL_Folder + "SQL_CustomerAccounts_{}.csv".format(self.date))
        DF_CustomerMaster = pd.read_csv(self.SQL_Folder + "SQL_CustomerMaster_{}.csv".format(self.date))
        DF_Complaints = pd.read_csv(self.SQL_Folder + "SQL_Complaints_{}.csv".format(self.date))
        dataframes = [DF_Trip, DF_TripHeader, DF_CustomerAccounts, DF_CustomerMaster, DF_Complaints]
        print('Dataframes stored')

        return dataframes