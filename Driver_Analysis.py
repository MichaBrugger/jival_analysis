import pyodbc
import pandas as pd
import numpy as np
import time
from datetime import date, datetime
from functools import reduce
import os
import glob

# To establish this connection:
# 1. Download and install ODBC Driver 17
# 2. Add connection in ODBC-Datasource Manager with following SQL Sever authentification credentials: UID: jvl_readonly, PW:jvl@@1

Conn_SQL = pyodbc.connect(
    'DSN=Jivana_Vitality; UID=jvl_readonly; PWD=jvl@@1;Trusted_Connection=no')  # establishing connection with the pyodbc library

SQL_TripHeader = """
    select 
    th_id as 'Trip_Header_ID', 
    convert(smalldatetime,TH_Trip_Date,102) as 'Trip_Date', 
    th_shop_description as 'Shop_Name', 
    th_route_description as 'Route_Name', 
    convert(smalldatetime,first_load_time,108) as 'Trip_StartTime', 
    convert(smalldatetime,driver_completed_datetime,108) as 'Trip_EndTime', 
    TD.[Actual_Delivery], 
    EM_Employee_First_Name + ' ' + EM_Employee_Last_Name 'Driver_Name',
    TL_Join.[Article_Quantity]
    from JL_Trip_Header TH 
    inner join( 
        select tl.TL_Header_ID, 
        sum(tl_quantity) as 'Article_Quantity', 
        TL2.TL_FirstLoad as 'First_Load_Time' 
        from JL_Trip_Load TL 
        inner join(
            select TL_Header_ID, 
            Min(tl_date) as TL_FirstLoad 
            from JL_Trip_Load 
            where TL_Active_Flage = '1' 
            group by TL_Header_ID) TL2 
        on TL.TL_Header_ID = TL2.tl_header_id and tl.TL_Date = tl2.TL_FirstLoad 
        group by tl.TL_Header_ID, tl2.TL_FirstLoad) TL_Join 
    on TH.TH_ID = TL_join.TL_Header_ID 
    inner join(
        select td_trip_header_id, 
        sum(TD_Actual_delivered_qty) as 'Actual_Delivery' 
        from jl_trip_details 
        where TD_Active_Flag = '1' 
        and td_trip_completed = '1' 
        group by td_trip_header_id) TD 
    on TD.TD_Trip_Header_ID = TL_Join.TL_Header_ID 
    
    inner join jl_employee_master EM
    on TH.TH_Driver_Employee_ID = EM_Employee_ID
    
    where TH_Trip_Date > DATEADD(day,-14,getdate()) 
        and TH_Active_Flag = '1' 
        and th_route_description not like 'OT Route'
        and ((DATEPART(dw, TH_Trip_Date) + @@DATEFIRST) % 7) NOT IN (1) 
        and IS_RECONCILED = '1' 
        and th_active_flag = '1' 
        and th_route_description != 'OT Route' 
        and IS_DRIVER_COMPLETED = '1' 
        and TH_Trip_Completed = '1'
    """

SQL_Trip = """
    select
        td_date 'Date',
        TD_Shop_Description 'Shop',
        TD_Route_Description 'Route',
        sum(TD_Planned_Delivery_Qty) 'Planned_Delivery',
        sum(TD_Actual_Delivered_Qty) 'Actual_Delivery',
        EM_Employee_First_Name + ' ' + EM_Employee_Last_Name 'Driver',
        sum(case when (TD_Planned_Delivery_Qty > 0 and TD_Actual_Delivered_Qty = 0) then 1 else 0 end) 'Zero_Delivery'

    from JL_Trip_Details TD

    inner join JL_Trip_Header TH
    on TD_Trip_Header_ID = TH.TH_ID

    inner join jl_employee_master EM
    on TH.TH_Driver_Employee_ID = EM_Employee_ID

    where TD_Active_Flag = '1'
        and td_route_description not like 'OT Route'
        and TD_Trip_Completed = '1'
        and th.TH_Active_Flag = '1'
        and th.TH_Trip_Completed = '1'
        and th.TH_Trip_Status = 'confirmed'
        and ((DATEPART(dw, TD_Date) + @@DATEFIRST) % 7) NOT IN (1) 
        and td_date > DATEADD(day,-14,getdate())
    group by TD_Date, TD_Shop_Description, TD_Route_Description, EM_Employee_First_Name + ' ' + EM_Employee_Last_Name
"""

Queries = {"SQL_TripHeader": SQL_TripHeader, "SQL_Trip": SQL_Trip}
SQL_Folder = 'SQL_RawData/'
Date = str(date.today())

# While working in India we often had the problem that our internet would just stop working for a few hours
# so I decided to store the content of the queries locally, so if I was able to access the data at least
# once a day, I was still able work with the data for the rest of that day. In addition to this it made re-
# peated runs of the code faster.

# At the same time I had to make sure that I dont use old data accidentally. So I wrote the code in a way
# that it always deletes old files of the same file path/name but with a different date/ending. Also other
# files with totally different names are left untouched, in case someone stores something different in the
# folder.

def get_data_from_sql():
    if not os.path.exists(SQL_Folder):
        os.makedirs(SQL_Folder)
    for Query_Name, Query in Queries.items():
        global csv_name
        csv_name = '{}_'.format(Query_Name) + Date + '.csv'
        if not os.path.exists(SQL_Folder + csv_name):
            for filename in glob.glob("{0}{1}_*".format(SQL_Folder, Query_Name)):
                try:
                    os.remove(filename)
                    print('{} removed'.format(filename))
                except:
                    print('Remove {} is not possible'.format(Query_Name))
            pd.read_sql_query(Query, Conn_SQL).to_csv(SQL_Folder + csv_name)
            print('{} downloaded successful'.format(Query_Name))
        else:
            print('{} already downloaded'.format(Query_Name))


get_data_from_sql()

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
        if not os.path.exists(Shop_List[Shop]):
            os.makedirs(Shop_List[Shop])
        df_shop = (df_final.loc[df_final['Shop']==ShopName])
        df_shop.to_csv(ShopName + '/{}_{}.csv'.format(ShopName, Date), index=False)
        df_shop.to_html(ShopName + '/{}_{}.html'.format(ShopName, Date), index=False)

    # Saving a final overview in csv and html
    df_final.to_csv("Overview_{}.csv".format(Date), index=False)
    df_final.to_html("Overview_{}.html".format(Date), index=False)

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