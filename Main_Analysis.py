import pandas as pd
from datetime import date, datetime
from functools import reduce
from SQL_Queries import SQL_Queries
from Data_from_SQL import get_Data
from Save_Output import Save_Output

# Calling the stored SQL_Queries and saving them into a dictionary
Call_SQL_Queries = SQL_Queries()
Queries = {"SQL_TripHeader": Call_SQL_Queries.SQL_TripHeader, "SQL_Trip": Call_SQL_Queries.SQL_Trip}

SQL_Folder = 'Output/SQL_RawData/'
date = str(date.today())

#
Call_Get_Data = get_Data(SQL_Folder, Queries, date)
Call_Get_Data.get_data_from_sql()


def convert_sec_to_time(x):
    # convert seconds into hours:minutes
    t = int(x)
    day = t // 86400
    hour = (t - (day * 86400)) // 3600
    minute = (t - ((day * 86400) + (hour * 3600))) // 60
    return "{0}:{1}".format(hour, minute)


def days_between(d1, d2):
    # calculate absolute time difference between start and end trip in second format
    d1 = datetime.strptime(d1, "%Y-%m-%d %H:%M:%S")
    d2 = datetime.strptime(d2, "%Y-%m-%d %H:%M:%S")
    return (abs(d2 - d1).seconds)


def operations_on_csv():
    # main calculations/merging of different dataframes from csv-files
    dataframes = Call_Get_Data.store_csv_to_df()
    DF_Trip = dataframes[0]
    DF_TripHeader = dataframes[1]

    # ad stands for Actual Delivery, pd stands for Planned Delivery and zero stands for Zero Delivery (Planned Delivery > 0 and Actual Delivery = 0)
    df_mean_ad = DF_Trip.groupby(['Shop','Route', 'Driver'], as_index=False)['Actual_Delivery'].mean().round(1)
    df_mean_ad.columns = ['Shop','Route','Driver','Avg Delivery']
    df_mean_zero = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Zero_Delivery'].mean().round(1)
    df_min = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].min()
    df_max = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].max()
    df_count = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].count()
    df_sum = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].sum()
    df_mean_pd = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Planned_Delivery'].mean().round(1)

    # Establishing final dataframe from
    df_final = reduce(lambda left, right: pd.merge(left, right, on=['Route', 'Driver']),
                     [df_count, df_sum, df_mean_zero, df_mean_ad, df_mean_pd, df_min, df_max])

    # apply function to calculate delivery time for calculating avg delivery time
    DF_TripHeader['Delivery_time'] = DF_TripHeader.apply(lambda row: (int(days_between(row.Trip_StartTime, row.Trip_EndTime))), axis=1)
    DF_TripHeader['Delivery_time'] = DF_TripHeader['Delivery_time'].fillna(0)

    # Calculating average delivery time per route/driver and converting into h:m format using convert_sec_to_time()
    df_time_mean = DF_TripHeader.groupby(['Route_Name'], as_index=False)['Delivery_time'].mean()
    df_time_mean['avg_delivery_time'] = df_time_mean.apply(lambda row: (convert_sec_to_time(row.Delivery_time)), axis=1)

    # Outer joining the df_final with the df_time_mean based on the route value.
    # Using the outer join in case there is any difference between the two data sources (technically shouldn't happen)
    # I would still have all the data in my frame
    df_final = pd.merge(df_final, df_time_mean, how='outer', left_on=['Route'], right_on=['Route_Name'])

    # Calculating the average amount of Vessels delivered per hour
    df_final['Avg Del/h'] = (df_final['Avg Delivery'] / (df_final['Delivery_time']/3600)).round(2)
    df_final['0 Delivery %'] = (df_final['Zero_Delivery']/df_final['Avg Delivery']).round(1)

    # Dropping columns that are not needed at this point anymore
    df_final = df_final.drop(['Delivery_time', 'Route_Name'], axis=1)

    # Renaming the the columns with proper names and rearranging them in logical order
    df_final.columns = ['Route', 'Driver', 'Amount of Trips', 'Total Deliveries', 'Avg 0 Delivery','Shop', 'Avg Delivery', 'Avg Planned',
                        'Min Delivery', 'Max Delivery', 'Avg Time', 'Avg Del/h', '0 Delivery %']
    df_final = df_final[['Shop','Route','Driver','Total Deliveries','Amount of Trips','Avg Delivery','Avg Planned',
                         'Min Delivery', 'Max Delivery', 'Avg Time', 'Avg Del/h','Avg 0 Delivery','0 Delivery %']]

    # Sorting the values for better overview
    df_final = df_final.sort_values(['Shop', 'Route', 'Amount of Trips'], ascending=False)

    # splitting (by shop) and saving the output-dataframes
    save = Save_Output(date, df_final)
    save.save_to_folder()


operations_on_csv()