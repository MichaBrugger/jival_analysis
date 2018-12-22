import pandas as pd
from datetime import date, datetime
from functools import reduce
from SQL_Queries import SQL_Queries
from Data_from_SQL import get_Data
from Save_Output import Save_Output

"""
The following code is meant to be the baseline for a future driver and route analysis for Jivana Vitality. I wrote it
during my internship as a project for the HSG XCamp course. While the current version is not yet capable of the in-depth
analysis that is the goal for the future, it already serves as an overview for both managers and executives to see how
certain routes and drivers are performing.

To add some context to the project:
Jivana Vitality India Pvt. Ltd. is an Indian for-profit company providing affordable drinking water. It was founded in
2014 by three HSG Students and has since established itself as the biggest water provider in Udaipur, India.
In both rural and urban parts of India access to affordable, clean drinking water is still a big problem and many people
have problems with diseases caused by polluted water. Jivana Vitality tackles this problem by providing bottle -water
quality water for the fraction of the price that bottled water costs, thus making it affordable for everyone. Through five
water-shops in Udaipur we deliver 80'000 liters of water daily to over 5000 active customers directly to their doorstep.

With around 35 routes, each 'driven' by multiple drivers, a performance overview is getting more and more difficult. In
addition Jivana is currently planning expansions to other cities, which makes a automated performance analysis a must.
"""

# Calling the stored SQL_Queries and saving them into a dictionary
Call_SQL_Queries = SQL_Queries()
Queries = {"SQL_TripHeader": Call_SQL_Queries.SQL_TripHeader, "SQL_Trip": Call_SQL_Queries.SQL_Trip}

SQL_Folder = 'Output/SQL_Data/'
date = str(date.today())

# Pulling the data from SQL, storing it into a csv and read that csv into a dataframe. Following args needed:
# # SQL_Folder - Folder where the raw data gets stored and accessed from
# # Queries - Dictionary, containing name and code of the queries
# # date - today's date as a string
Call_Get_Data = get_Data(SQL_Folder, Queries, date)
Call_Get_Data.get_data_from_sql()


def convert_sec_to_time(x):
    # Convert seconds into hours:minutes
    t = int(x)
    day = t // 86400
    hour = (t - (day * 86400)) // 3600
    minute = (t - ((day * 86400) + (hour * 3600))) // 60
    return "{0}:{1}".format(hour, minute)


def days_between(d1, d2):
    # Calculate absolute time difference between start and end trip in second format
    d1 = datetime.strptime(d1, "%Y-%m-%d %H:%M:%S")
    d2 = datetime.strptime(d2, "%Y-%m-%d %H:%M:%S")
    return abs(d2 - d1).seconds


def operations_on_csv():
    # Main calculations/merging of different dataframes from csv-files

    # Calling the stored dataframes
    dataframes = Call_Get_Data.store_csv_to_df()
    DF_Trip = dataframes[0]
    DF_TripHeader = dataframes[1]

    # ad stands for Actual Delivery, pd stands for Planned Delivery and zero stands for Zero Delivery (Planned Delivery > 0 and Actual Delivery = 0)
    df_mean_ad = DF_Trip.groupby(['Shop','Route', 'Driver'], as_index=False)['Actual_Delivery'].mean().round(1)
    df_mean_ad.columns = ['Shop','Route','Driver','Avg Delivery']
    df_mean_customers = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Customer_Count'].mean().round(1)
    df_mean_customers.columns = ['Route', 'Driver', 'Avg Customer Count']
    df_mean_zero = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Zero_Delivery'].mean().round(1)
    df_min = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].min()
    df_max = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].max()
    df_count = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].count()
    df_sum = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].sum()
    df_mean_pd = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Planned_Delivery'].mean().round(1)

    # Establishing final dataframe (to which later other dataframes and calculations will be added)
    df_final = reduce(lambda left, right: pd.merge(left, right, on=['Route', 'Driver']),
                     [df_count, df_sum, df_mean_zero, df_mean_ad, df_mean_pd, df_min, df_max, df_mean_customers])

    # apply function to calculate delivery time for calculating average delivery time
    # fill missing values with 0, so I dont run into an error if a trip is still ongoing and has no end-time yet
    DF_TripHeader['Delivery_time'] = DF_TripHeader.apply(lambda row: (int(days_between(row.Trip_StartTime, row.Trip_EndTime))), axis=1)
    DF_TripHeader['Delivery_time'] = DF_TripHeader['Delivery_time'].fillna(0)

    # Calculating average delivery time per route/driver
    df_time_mean = DF_TripHeader.groupby(['Shop_Name', 'Route_Name', 'Driver_Name'], as_index=False)['Delivery_time'].mean()

    # Calculating the average deliveries per hour before converting the average time to an hour:minute format
    df_final['Avg Delivery/h'] = (df_final['Avg Delivery'] / (df_time_mean['Delivery_time'])*3600).round(1)
    df_time_mean['avg_delivery_time'] = df_time_mean.apply(lambda row: (convert_sec_to_time(row.Delivery_time)), axis=1)

    # Outer joining the df_final with the df_time_mean based on the shop, route and driver value.
    # Using the outer join in case there is any difference between the two data sources (technically shouldn't happen)
    # I would still have all the data in my frame
    df_final = pd.merge(df_final, df_time_mean, how='outer',
                        left_on=['Shop', 'Route', 'Driver'], right_on=['Shop_Name', 'Route_Name', 'Driver_Name'])

    # Calculating the percentage average amount of 0 deliveries
    # Done by taking the average amount of 0 deliveries divided by the average amount of customers for this route
    df_final['0 Delivery (%)'] = (df_final['Zero_Delivery']/df_final['Avg Customer Count']*100).round(1)

    # Dropping columns that are not needed at this point anymore
    df_final = df_final.drop(['Shop_Name', 'Delivery_time', 'Route_Name', 'Avg Customer Count', 'Driver_Name'], axis=1)

    # Renaming the the columns with proper names and rearranging them in logical order
    df_final.columns = ['Route', 'Driver', 'Amount of Trips', 'Total Deliveries', 'Avg 0 Delivery', 'Shop', 'Avg Delivery',
                        'Avg Planned', 'Min Delivery', 'Max Delivery', 'Avg Delivery/h', 'Avg Time (h:m)', 'Avg 0 Delivery (%)']
    df_final = df_final[['Shop', 'Route', 'Driver', 'Amount of Trips', 'Avg Planned', 'Avg Delivery', 'Avg 0 Delivery (%)',
                         'Avg Delivery/h', 'Avg Time (h:m)', 'Total Deliveries', 'Min Delivery', 'Max Delivery', 'Avg 0 Delivery']]

    # Sorting the values for better overview
    df_final = df_final.sort_values(['Shop', 'Route', 'Amount of Trips'], ascending=False)

    # splitting (by shop) and saving the output-dataframes. Following args needed:
    # # date - today's date as a string
    # df_final - final dataframe that contains all data that is to be displayed
    save = Save_Output(date, df_final)
    save.save_to_folder()


operations_on_csv()
