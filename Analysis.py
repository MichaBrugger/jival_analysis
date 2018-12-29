import pandas as pd
from functools import reduce
from datetime import datetime


def days_between(d1, d2):
    # Calculate absolute time difference between start and end trip in second format
    d1 = datetime.strptime(d1, "%Y-%m-%d %H:%M:%S")
    d2 = datetime.strptime(d2, "%Y-%m-%d %H:%M:%S")
    return abs(d2 - d1).seconds


def convert_sec_to_time(x):
    # Convert seconds into hours:minutes
    t = int(x)
    day = t // 86400
    hour = (t - (day * 86400)) // 3600
    minute = (t - ((day * 86400) + (hour * 3600))) // 60
    return "{0}:{1}".format(hour, minute)


class Analysis:

    def __init__(self, DF_Trip, DF_TripHeader, DF_CustomerAccounts, DF_Complaints, DF_CustomerMaster):

        self.DF_Trip = DF_Trip
        self.DF_TripHeader = DF_TripHeader
        self.DF_CustomerAccounts = DF_CustomerAccounts
        self.DF_Complaints = DF_Complaints
        self.DF_CustomerMaster = DF_CustomerMaster

    def calc(self):

        # target indicates by what level the data should be aggregated
        # its possible to aggregate by a single level (f.e. 'Shop') or multiple levels (f.e. 'Shop', 'Driver')
        # this will later be implemented in the GUI
        target = ['Driver']

# ----- Calculations regarding the DF_Trip

        trip_avg = self.DF_Trip.groupby(target, as_index=False)['Actual_Delivery', 'Zero_Delivery', 'Customer_Count'].mean().round(1)
        trip_count = self.DF_Trip.groupby(target, as_index=False)['Actual_Delivery'].count()
        trip_sum = self.DF_Trip.groupby(target, as_index=False)['Actual_Delivery'].sum()

        # Merging the values from DF_Trip into one DF_Trip_M(erged) and renaming the columns
        DF_Trip_M = reduce(lambda left, right: pd.merge(left, right, on=target),[trip_avg, trip_count, trip_sum])
        DF_Trip_M.columns = target + ['Ø Del', 'Ø 0 Del', 'Customers','# Trips', 'Total Del']

        # Calculating the percentage average amount of 0 deliveries and dropping unneeded columns
        DF_Trip_M['0 Del (%)'] = (DF_Trip_M['Ø 0 Del'] / DF_Trip_M['Customers'] * 100).round(1)
        DF_Trip_M.drop(['Ø 0 Del', 'Customers'], axis=1)

# ----- Calculations regarding the DF_TripHeader

        # Apply function to calculate delivery per trip
        self.DF_TripHeader['Delivery_time'] = self.DF_TripHeader.apply(lambda row:(int(days_between(row.Trip_StartTime,row.Trip_EndTime))),axis=1)

        # Grouping DF_TripHeader by target and storing into new DF_TripHeader_M(erged)
        DF_TripHeader_M = self.DF_TripHeader.groupby(target, as_index=False)['Delivery_time'].mean().round(1)

        # Merging DF_Trip_M and DF_TripHeader_M into new DF Output_Raw
        Output_Raw = DF_Trip_M.merge(DF_TripHeader_M, on=target, how='left')

        # Calculating Avg Time and Avg Del/h then dropping Delivery_time
        Output_Raw['Ø Time'] = Output_Raw.apply(lambda row: (convert_sec_to_time(row.Delivery_time)), axis=1)
        Output_Raw['Ø Del/h'] = ((Output_Raw['Ø Del'] / (Output_Raw['Delivery_time'])) * 3600).round(1)
        Output_Raw = Output_Raw.drop(['Delivery_time'], axis=1)

#------ Calculations regarding the DF_CustomerAccounts

        # Customer Accounts (Outstanding Amount per Route) can only be merged on shop and route level
        # If the aggregation is on driver level this wont be executed
        try:
            # Grouping by target and then merging with Output_Raw
            self.DF_CustomerAccounts = self.DF_CustomerAccounts.groupby(target, as_index=False)['Open Invoices'].sum()
            Output_Raw = Output_Raw.merge(self.DF_CustomerAccounts['Open Invoices'], how='left', on=target)

            # Column formatting (currency) for better visibility
            Output_Raw['Open Invoices'] = Output_Raw['Open Invoices'].map(lambda x: "INR {0:,.0f}".format(x))
        except:
            pass

#------ Calculations regarding the DF_Customer_Master

        # Grouping by target and then merging with Output_Raw
        self.DF_CustomerMaster = self.DF_CustomerMaster.groupby(target, as_index=False)['# New Customers'].sum()
        Output_Raw = Output_Raw.merge(self.DF_CustomerMaster, how='left', on=target)

#------ Calculations regarding the DF_Complaints

        # Grouping by target and then merging with Output_Raw
        self.DF_Complaints = self.DF_Complaints.groupby(target, as_index=False)['Total Complaints', 'Closed Complaints'].sum()
        Output_Raw = Output_Raw.merge(self.DF_Complaints, how='left', on=target)

        # Calculating the percentage of closed complaints and then droping 'Closed Complaints'
        Output_Raw['Closed (%)'] = (Output_Raw['Closed Complaints']/Output_Raw['Total Complaints']*100).round(1)
        Output_Raw = Output_Raw.drop(['Closed Complaints'], axis=1)

#------ Basic formatting and returning Output_Raw to Main

        Output_Raw = Output_Raw.fillna('')

        return Output_Raw
