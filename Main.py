import pandas as pd
from datetime import date
from QueriesSQL import SQL_Queries
from StoreData import get_Data
from SaveOutput import Save_Output
from Analysis import Analysis
from Ranking import Ranking

"""
The following code is meant to be the baseline for a future driver and route analysis for Jivana Vitality. I wrote it
during my internship as a project for the HSG XCamp course. While the current version is not yet capable of the in-depth
analysis that is the goal for the future, it  already serves as an overview for both managers and executives to see how
certain routes and drivers are performing.

To add some context to the project:
Jivana Vitality India Pvt. Ltd. is an Indian for-profit company providing affordable drinking water. It was founded in
2014 by three HSG Students and has since established itself as the biggest water provider in Udaipur, India.
In both rural and urban parts of India access to affordable, clean drinking water is still a big problem and many people
have problems with diseases caused by polluted water. Jivana Vitality tackles this problem by providing bottled - water
quality water for a fraction of the price that bottled water costs, thus making it affordable for everyone. Through five
water-shops in Udaipur we deliver 80'000 liters of water daily to over 5000 active customers directly to their doorstep.

With around 35 routes, each 'driven' by multiple drivers, a performance overview is getting more and more difficult. In
addition Jivana is currently planning expansions to other cities, which makes a automated performance analysis a must.
"""

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

        self.Call_Get_Data = get_Data(self.SQL_Folder, Queries, self.dateToday)
        self.Call_Get_Data.get_data_from_sql()

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


