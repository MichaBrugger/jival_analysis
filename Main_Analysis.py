import pandas as pd
from datetime import date, datetime
from functools import reduce
from SQL_Queries import SQL_Queries
from Data_from_SQL import get_Data
from Save_Output import Save_Output

Call_SQL_Queries = SQL_Queries()
Queries = {"SQL_TripHeader": Call_SQL_Queries.SQL_TripHeader, "SQL_Trip": Call_SQL_Queries.SQL_Trip}
SQL_Folder = 'Output/SQL_RawData/'
date = str(date.today())

Call_Get_Data = get_Data(SQL_Folder, Queries, date)

Call_Get_Data.get_data_from_sql()

# The function convert_sec_to_time converts seconds into hours:minutes
def convert_sec_to_time(x):
    t = int(x)
    day = t // 86400
    hour = (t - (day * 86400)) // 3600
    minute = (t - ((day * 86400) + (hour * 3600))) // 60
    return "{0}:{1}".format(hour, minute)

# function days_between to calculate absolute time difference between start and end trip in second format.
def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d %H:%M:%S")
    d2 = datetime.strptime(d2, "%Y-%m-%d %H:%M:%S")
    return (abs(d2 - d1).seconds)

# operations_on_csv function to perform operation on csv datasheet
def operations_on_csv():

    dataframes = Call_Get_Data.store_csv_to_df()
    DF_Trip = dataframes[0]
    DF_TripHeader = dataframes[1]

    # apply function to calculate Delivery time for calculating avg delivery time
    DF_TripHeader['Delivery_time'] = DF_TripHeader.apply(
        lambda row: (int(days_between(row.Trip_StartTime, row.Trip_EndTime))), axis=1)

    # The ad stands for Actual Delivery, pd stands for Planned Delivery and Zero stands for Zero Delivery (Planned Delivery > 0 and Actual Delivery = 0)
    df_mean_ad = DF_Trip.groupby(['Shop','Route', 'Driver'], as_index=False)['Actual_Delivery'].mean().round(1)
    df_mean_ad.columns = ['Shop','Route','Driver','Avg Delivery']
    df_mean_zero = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Zero_Delivery'].mean().round(1)
    df_min = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].min()
    df_max = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].max()
    df_count = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].count()
    df_sum = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].sum()
    df_mean_pd = DF_Trip.groupby(['Route', 'Driver'], as_index=False)['Planned_Delivery'].mean().round(1)

    df_final = reduce(lambda left, right: pd.merge(left, right, on=['Route', 'Driver']),
                     [df_count, df_sum, df_mean_zero, df_mean_ad, df_mean_pd, df_min, df_max])

    # Filling NaN value with the value '0' to avoid errors
    DF_TripHeader['Delivery_time'] = DF_TripHeader['Delivery_time'].fillna(0)

    df_time_mean = DF_TripHeader.groupby(['Route_Name'], as_index=False)['Delivery_time'].mean()

    # calculating average delivery time and converting into hours:minute format using convert_sec_to_time()
    df_time_mean['avg_delivery_time'] = df_time_mean.apply(lambda row: (convert_sec_to_time(row.Delivery_time)), axis=1)

    # Outer joining the df_final with the df_time_mean based on the route value. Using the outer join in case
    # there is any difference between the two data source points (technically shouldn't happen) I would still have
    # all the data in my frame
    df_final = pd.merge(df_final, df_time_mean, how='outer', left_on=['Route'], right_on=['Route_Name'])

    #Calculating the average amount of Vessels delivered per hour
    df_final['Avg Del/h'] = (df_final['Avg Delivery'] / (df_final['Delivery_time']/3600)).round(2)

    df_final['0 Delivery %'] = (df_final['Zero_Delivery']/df_final['Avg Delivery']).round(1)

    # Droping columns that are not needed at this point anymore, so I can also avoid renaming them for nothing
    df_final = df_final.drop(['Delivery_time', 'Route_Name'], axis=1)

    # Renaming the columns with proper names
    df_final.columns = ['Route', 'Driver', 'Amount of Trips', 'Total Deliveries', 'Zero_Delivery','Shop', 'Avg Delivery', 'Avg Planned',
                        'Min Delivery', 'Max Delivery', 'Avg Time', 'Avg Del/h', '0 Delivery %']

    # Rearranging the columns in a more intuitive order
    df_final = df_final[['Shop','Route','Driver','Total Deliveries','Amount of Trips','Avg Delivery','Avg Planned',
                         'Min Delivery', 'Max Delivery', 'Avg Time', 'Avg Del/h','Zero_Delivery','0 Delivery %']]

    #Sorting the values for better Overview
    df_final = df_final.sort_values(['Shop', 'Route', 'Amount of Trips'], ascending=False)

    """

    # performing operations using lambda function and groupby to sort based upon shop and driver (calculating number of zeroes in actual delivery)
    df_count = DF_Trip.groupby(['Route'])['Actual_Delivery'].apply(lambda x: (x == 0).sum()).reset_index(name='zero_count')

    df_final = reduce(lambda left, right: pd.merge(left, right, on=['Route']), [df_final, df_count])

    # empty list to store zero deliver percentage
    perlist = []

    # operation to calculate zero delivery % for driver
    for i in range(len(df_final['zero_count'])):
        perlist.append({'per_zero_count': (((df_final['zero_count'][i]) / (df_final['Total Deliveries'][i]) * 100))})
    
    # convert list to dataframe and then concate with df_count dataframe which is master dataframe
    df_final = pd.concat([df_final, pd.DataFrame(perlist)], axis=1)

    """

    Save = Save_Output(date, df_final)
    Save.Save_to_Folder()


    # Help Section -------
    # https://ourcodeworld.com/articles/read/240/how-to-edit-and-add-environment-variables-in-windows-for-easy-command-line-access
    # https://www.odoo.com/forum/help-1/question/unable-to-find-wkhtmltopdf-on-this-system-the-report-will-be-shown-in-html-63900

operations_on_csv()