import pandas as pd
from datetime import date
from QueriesSQL import SQL_Queries
from StoreData import get_Data
from SaveOutput import Save_Output
from Analysis import Analysis
from Ranking import Ranking


class Main:

    Call_Get_Data = None
    dateToday = str(date.today())
    SQL_Folder = 'Output/SQL_Data/'

    def operations_on_csv(self, daysback):

        # Calling the stored SQL_Queries and saving them into a dictionary
        Call_SQL_Queries = SQL_Queries(daysback)

        Queries = {"SQL_TripHeader": Call_SQL_Queries.SQL_TripHeader,
                   "SQL_Trip": Call_SQL_Queries.SQL_Trip,
                   "SQL_CustomerAccounts": Call_SQL_Queries.SQL_CustomerAccounts,
                   "SQL_CustomerMaster": Call_SQL_Queries.SQL_CustomerMaster,
                   "SQL_Complaints": Call_SQL_Queries.SQL_Complaints,
                   "SQL_EmployeeMaster": Call_SQL_Queries.SQL_EmployeeMaster,
                   "SQL_Receipts": Call_SQL_Queries.SQL_Receipts}

        # Pulling the data from SQL, storing it into a csv and read that csv into a dataframe. Following args needed:
        # SQL_Folder - Folder where the raw data gets stored and accessed from
        # Queries - Dictionary, containing name and code of the queries
        # date - today's date as a string
        Call_Get_Data = get_Data(self.SQL_Folder, Queries, self.dateToday)
        Call_Get_Data.get_data_from_sql()


    def calculations(self, target, betterScore, Bonus):
        # Main calculations/merging of different data frames from csv-files

        # Calling the stored data frames
        dataframes = self.Call_Get_Data.store_csv_to_df()
        DF_Trip = dataframes[0]
        DF_TripHeader = dataframes[1]
        DF_CustomerAccounts = dataframes[2]
        DF_CustomerMaster = dataframes[3]
        DF_Complaints = dataframes[4]
        DF_EmployeeMaster = dataframes[5]
        DF_Receipts = dataframes[6]

        # Executing Analysis to get Output_Raw based on aggregation level(target)
        getRaw = Analysis(DF_Trip, DF_TripHeader, DF_CustomerAccounts, DF_Complaints, DF_CustomerMaster,
                          DF_EmployeeMaster, DF_Receipts)
        Output_Raw = getRaw.calc(target)

        # Making sure the data is actually numeric and not formatted as an object
        Output_Raw = Output_Raw.apply(pd.to_numeric, errors='ignore')

        # Executing Ranking to get Output_Ranked out of Output_Raw
        getRanked = Ranking(Output_Raw)
        Output_Ranked = getRanked.rank(target, betterScore, Bonus)

        # splitting by shop and saving the output-data frames. Following args needed:
        # # date - today's date as a string
        # df_final - final data frame that contains all data that is to be displayed
        save = Save_Output(self.dateToday, Output_Raw, Output_Ranked)
        save.save_to_folder()

