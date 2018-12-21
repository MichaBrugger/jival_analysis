import pandas as pd
import os
import numpy as np
import time
from datetime import date, datetime
from functools import reduce
from SQL_Queries import SQL_Queries
from Get_SQL_Data_From_Files import get_Data

Call_SQL_Queries = SQL_Queries()
Queries = {"SQL_TripHeader": Call_SQL_Queries.SQL_TripHeader, "SQL_Trip": Call_SQL_Queries.SQL_Trip}
SQL_Folder = 'Output/SQL_RawData/'
Date = str(date.today())


Call_Get_Data = get_Data(SQL_Folder, Queries, Date)

Call_Get_Data.get_data_from_sql()

# store_csv_to_df function to take csv into dataframe
def store_csv_to_df():
    global dataframe_one
    global dataframe_two
    # Read data from file 'SQL_Trip_2018-12-16.csv'
    # (in the same directory that your python process is based)
    # Control delimiters, rows, column names with read_csv (see later)
    dataframe_one = pd.read_csv(SQL_Folder + "SQL_Trip_{}.csv".format(Date))
    dataframe_two = pd.read_csv(SQL_Folder + "SQL_TripHeader_{}.csv".format(Date))


# calling store_csv_to_df() function
store_csv_to_df()


# function convert_sec_to_time to convert seconds into hours:minutes
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
    # sec=get_sec(abs(d2 - d1))
    return (abs(d2 - d1).seconds)


# operations_on_csv function to perform operation on csv datasheet
def operations_on_csv():
    # apply function to calculate Delivery time for calculating avg delivery time
    dataframe_two['Delivery_time'] = dataframe_two.apply(
        lambda row: (int(days_between(row.Trip_StartTime, row.Trip_EndTime))), axis=1)

    df_mean_ad = dataframe_one.groupby(['Shop','Route', 'Driver'], as_index=False)['Actual_Delivery'].mean().round(1)
    df_mean_ad.columns = ['Shop','Route','Driver','Avg Delivery']
    df_mean_zero = dataframe_one.groupby(['Route', 'Driver'], as_index=False)['Zero_Delivery'].mean().round(1)
    df_min = dataframe_one.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].min()
    df_max = dataframe_one.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].max()
    df_count = dataframe_one.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].count()
    df_sum = dataframe_one.groupby(['Route', 'Driver'], as_index=False)['Actual_Delivery'].sum()
    df_planned_mean = dataframe_one.groupby(['Route', 'Driver'], as_index=False)['Planned_Delivery'].mean().round(1)

    df_final = reduce(lambda left, right: pd.merge(left, right, on=['Route', 'Driver']),
                     [df_count, df_sum, df_mean_zero, df_mean_ad, df_planned_mean, df_min, df_max])

    # Filling NaN value with the value '0' to avoid errors
    dataframe_two['Delivery_time'] = dataframe_two['Delivery_time'].fillna(0)

    df_time_mean = dataframe_two.groupby(['Route_Name'], as_index=False)['Delivery_time'].mean()

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
    df_count = dataframe_one.groupby(['Route'])['Actual_Delivery'].apply(lambda x: (x == 0).sum()).reset_index(name='zero_count')

    df_final = reduce(lambda left, right: pd.merge(left, right, on=['Route']), [df_final, df_count])

    # empty list to store zero deliver percentage
    perlist = []

    # operation to calculate zero delivery % for driver
    for i in range(len(df_final['zero_count'])):
        perlist.append({'per_zero_count': (((df_final['zero_count'][i]) / (df_final['Total Deliveries'][i]) * 100))})
    
    # convert list to dataframe and then concate with df_count dataframe which is master dataframe
    df_final = pd.concat([df_final, pd.DataFrame(perlist)], axis=1)

    """


    # Getting a unique list of all the shops in the data
    Shop_List = df_final['Shop'].unique()

    # Looping through the Shop_List, to create individual files/folders for every shop
    for Shop in range(len(Shop_List)):
        ShopName = Shop_List[Shop]
        df_shop=[]
        if not os.path.exists('Output/' + Shop_List[Shop]):
            os.makedirs('Output/' + Shop_List[Shop])
        df_shop = (df_final.loc[df_final['Shop']==ShopName])
        df_shop.to_csv('Output/' + ShopName + '/{}_{}.csv'.format(ShopName, Date), index=False)
        df_shop.to_html('Output/' + ShopName + '/{}_{}.html'.format(ShopName, Date), index=False)

    # Saving a final overview in csv and html
    df_final.to_csv('Output/' + "Overview_{}.csv".format(Date), index=False)
    df_final.to_html('Output/' + "Overview_{}.html".format(Date), index=False)

    # saving to csv file
    #df_final.to_html("output.html", show_dimensions=True)

    # Help Section -------
    # https://ourcodeworld.com/articles/read/240/how-to-edit-and-add-environment-variables-in-windows-for-easy-command-line-access
    # https://www.odoo.com/forum/help-1/question/unable-to-find-wkhtmltopdf-on-this-system-the-report-will-be-shown-in-html-63900

    # PDF Section
    # highly recommended to go through above url to work this function as it is very unstable lib
    # converting html to pdf file
    #pdfkit.from_file('output.html', 'output.pdf')


# calling operations_on_csv() function
operations_on_csv()