import pandas as pd
from datetime import date
from SQL_Queries import SQL_Queries
from Data_from_SQL import get_Data
from Save_Output import Save_Output
from Calculations.Calc_Delivery import Calc_Delivery
from Calculations.Calc_Time import Calc_Time
from Analysis import Analysis

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

# Calling the stored SQL_Queries and saving them into a dictionary
Call_SQL_Queries = SQL_Queries()
Queries = {"SQL_TripHeader": Call_SQL_Queries.SQL_TripHeader, "SQL_Trip": Call_SQL_Queries.SQL_Trip,
           "SQL_CustomerAccounts": Call_SQL_Queries.SQL_CustomerAccounts, "SQL_CustomerMaster": Call_SQL_Queries.get_SQL_CustomerMaster(),
           "SQL_Complaints": Call_SQL_Queries.SQL_Complaints}

SQL_Folder = 'Output/SQL_Data/'
date = str(date.today())

# Pulling the data from SQL, storing it into a csv and read that csv into a dataframe. Following args needed:
# SQL_Folder - Folder where the raw data gets stored and accessed from
# Queries - Dictionary, containing name and code of the queries
# date - today's date as a string
Call_Get_Data = get_Data(SQL_Folder, Queries, date)
Call_Get_Data.get_data_from_sql()

def operations_on_csv():
    # Main calculations/merging of different data frames from csv-files

    # Calling the stored data frames
    dataframes = Call_Get_Data.store_csv_to_df()
    DF_Trip = dataframes[0]
    DF_TripHeader = dataframes[1]
    DF_CustomerAccounts = dataframes[2]
    DF_CustomerMaster = dataframes[3]
    DF_Complaints = dataframes[4]

    """
    Since there are more and more calculations coming and I started to lose the overview, so I decided to split
    each data source with its calculations into its own class, so I only call the final 'clean' data frame for each
    data source into my main file. Here I finally perform the calculations where data sources 'interact' with each
    other. This makes it easier to perform changes on the individual data frames and makes the whole thing more
    structured for me. Other Data (that is already in the needed format) I join directly.
    """

    Call_Calc_Delivery = Calc_Delivery(DF_Trip)
    df_delivery = Call_Calc_Delivery.calc()

    Call_Calc_Time = Calc_Time(DF_TripHeader)
    df_time = Call_Calc_Time.calc()

    # Inner joining df_delivery and df_time based on the shop, route and driver value and establishing final data frame
    df_final = pd.merge(df_delivery, df_time, how='inner',
                        left_on=['TD_Shop', 'TD_Route', 'TD_Driver'], right_on=['TH_Shop', 'TH_Route', 'TH_Driver'])

    # Dropping dublicated/unneeded columns from this merge
    df_final = df_final.drop(['TH_Shop', 'TH_Route', 'TH_Driver', 'Delivery_time'], axis=1)

    # Inner joining the outstanding customer invoices per route to the existing final data frame
    df_final = pd.merge(df_final, DF_CustomerAccounts, how='inner',
                        left_on=['TD_Shop', 'TD_Route'], right_on=['CA_Shop', 'CA_Route'])

    # Dropping duplicated columns from this merge
    df_final = df_final.drop(['CA_Shop', 'CA_Route'], axis=1)

    # Left joining the new customers per driver to the existing final data frame
    df_final = pd.merge(df_final, DF_CustomerMaster, how='left', left_on=['TD_Driver', 'TD_Shop', 'TD_Route'],
                        right_on=['CM_Driver', 'CM_Shop', 'CM_Route'])

    # Dropping duplicated columns from this merge
    df_final = df_final.drop(['CM_Driver', 'CM_Shop', 'CM_Route'], axis=1)

    # Left joining the complaints per driver/route to the existing final data frame
    df_final = pd.merge(df_final, DF_Complaints, how='left',
                        left_on=['TD_Shop', 'TD_Route', 'TD_Driver'], right_on=['COM_Shop', 'COM_Route', 'COM_Driver'])

    # Dropping dublicated columns from this merge
    df_final = df_final.drop(['COM_Shop', 'COM_Route', 'COM_Driver'], axis=1)

    # Performing Calculations that are only possible with the merged data frames
    # 1. Calculating the average deliveries per hour before converting the average time to an hour:minute format
    df_final['Ø Delivery/h'] = ((df_final['Ø Delivery'] / (df_time['Delivery_time']))*3600).round(1)

    # Sorting the values for better overview
    df_final = df_final.sort_values(['TD_Shop', 'TD_Route', 'Ø Delivery/h'], ascending=False)

    # Formatting certain columns for better readability
    df_final['Open Invoices'] = df_final['Open Invoices'].map(lambda x: "INR {0:,.0f}".format(x))
    df_final['# New Customers'] = df_final['# New Customers'].fillna('')
    df_final['Total Complaints'] = df_final['Total Complaints'].fillna('')
    df_final['Closed Complaints'] = df_final['Closed Complaints'].fillna('')

    #New Logic
    XXX = Analysis(DF_Trip, DF_TripHeader, DF_CustomerAccounts, DF_Complaints, DF_CustomerMaster)
    A = XXX.calc()
    print(A)

    # splitting by shop and saving the output-data frames. Following args needed:
    # # date - today's date as a string
    # df_final - final data frame that contains all data that is to be displayed
    save = Save_Output(date, df_final)
    save.save_to_folder()


operations_on_csv()
