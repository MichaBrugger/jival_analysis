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

    def __init__(self, DF_Trip, DF_TripHeader, DF_CustomerAccounts, DF_Complaints, DF_CustomerMaster, DF_EmployeeMaster,
                 DF_Receipts):

        self.DF_Trip = DF_Trip
        self.DF_TripHeader = DF_TripHeader
        self.DF_CustomerAccounts = DF_CustomerAccounts
        self.DF_Complaints = DF_Complaints
        self.DF_CustomerMaster = DF_CustomerMaster
        self.DF_EmployeeMaster = DF_EmployeeMaster
        self.DF_Receipts = DF_Receipts

    def calc(self, target):
    # All calculations that are needed to create Output_Raw, ordered by data frame

# ----- Calculations regarding the DF_Trip

        trip_avg = self.DF_Trip.groupby(target, as_index=False)['Actual_Delivery', 'Zero_Delivery', 'Customer_Count'].mean().round(1)
        trip_count = self.DF_Trip.groupby(target, as_index=False)['Actual_Delivery'].count()
        trip_sum = self.DF_Trip.groupby(target, as_index=False)['Actual_Delivery'].sum()

        # Merging the values from DF_Trip into one DF_Trip_M(erged) and renaming the columns
        DF_Trip_M = reduce(lambda left, right: pd.merge(left, right, on=target),[trip_avg, trip_count, trip_sum])
        DF_Trip_M.columns = target + ['Ø Del', 'Ø 0 Del', 'Customers','# Trips', 'Total Del']

        # Calculating the percentage average amount of 0 deliveries
        DF_Trip_M['0 Del (%)'] = (DF_Trip_M['Ø 0 Del'] / DF_Trip_M['Customers'] * 100).round(1)

# ----- Calculations regarding the DF_TripHeader

        # Apply function to calculate delivery per trip
        self.DF_TripHeader['Delivery_time'] = self.DF_TripHeader.apply(lambda row:(int(days_between(row.Trip_StartTime,row.Trip_EndTime))),axis=1)

        # Grouping DF_TripHeader by target and storing into new DF_TripHeader_M(erged)
        DF_TripHeader_M = self.DF_TripHeader.groupby(target, as_index=False)['Delivery_time'].mean().round(1)

        # Merging DF_Trip_M and DF_TripHeader_M into new DF Output_Raw
        Output_Raw = DF_Trip_M.merge(DF_TripHeader_M, on=target, how='left')

        # Calculating Avg Time and Avg Del/h
        Output_Raw['Ø Time'] = Output_Raw.apply(lambda row: (convert_sec_to_time(row.Delivery_time)), axis=1)
        Output_Raw['Ø Del/h'] = ((Output_Raw['Ø Del'] / (Output_Raw['Delivery_time'])) * 3600).round(1)

#------ Merging with DF_Receipts

        self.DF_Receipts = self.DF_Receipts.groupby(target, as_index=False)['Receipts'].sum()
        Output_Raw = Output_Raw.merge(self.DF_Receipts, how='left', on=target)

#------ Calculations regarding the DF_CustomerAccounts

        # Customer Accounts (Outstanding Amount per Route) can only be merged on shop and route level
        # If the aggregation is on driver level this wont be executed
        try:# Grouping by target and then merging with Output_Raw
            self.DF_CustomerAccounts = self.DF_CustomerAccounts.groupby(target, as_index=False)['Open Invoices'].sum()
            Output_Raw = Output_Raw.merge(self.DF_CustomerAccounts, how='left', on=target)
            Output_Raw['Collected (%)'] = ((Output_Raw['Receipts'] / Output_Raw['Open Invoices']) * 100).round(1)
        except: pass

#------ Calculations regarding the DF_Customer_Master

        # Grouping by target and then merging with Output_Raw
        self.DF_CustomerMaster = self.DF_CustomerMaster.groupby(target, as_index=False)['New Customers'].sum()
        self.DF_CustomerMaster.fillna('0')
        Output_Raw = Output_Raw.merge(self.DF_CustomerMaster, how='left', on=target)

#------ Calculations regarding the DF_Complaints

        # Grouping by target and then merging with Output_Raw
        self.DF_Complaints = self.DF_Complaints.groupby(target, as_index=False)['Complaints', 'Closed Complaints'].sum()
        Output_Raw = Output_Raw.merge(self.DF_Complaints, how='left', on=target)

        # Calculating the percentage of closed complaints
        Output_Raw['Closed (%)'] = (Output_Raw['Closed Complaints']/Output_Raw['Complaints']*100).round(1)

#------ Merging with DF_EmployeeMaster

        # Merging with Employee Master as late as possible, because driver ID's are unique, driver names are not
        if 'Driver_ID' in Output_Raw.columns:
            Output_Raw = self.DF_EmployeeMaster.merge(Output_Raw, on='Driver_ID', how='right')

            #replacing Driver_ID in target through 'Driver' using the index function
            target[target.index('Driver_ID')] = 'Driver'

#------ Basic formatting and returning Output_Raw to Main

        Output_Raw = Output_Raw.fillna('0')

        try:
            Output_Raw = Output_Raw[target + ['Total Del', '# Trips', 'Ø Del', 'Ø Del/h', 'Ø 0 Del', '0 Del (%)',
                                          'Customers', 'New Customers', 'Ø Time', 'Complaints', 'Closed (%)', 'Collected (%)']]
        except:
            Output_Raw = Output_Raw[target + ['Total Del', '# Trips', 'Ø Del', 'Ø Del/h', 'Ø 0 Del', '0 Del (%)',
                                          'Customers', 'New Customers', 'Ø Time', 'Complaints', 'Closed (%)', 'Receipts']]

        return Output_Raw
