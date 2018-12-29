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

        target = 'TD_Shop'

        trip_avg = self.DF_Trip.groupby([target], as_index=False)['Actual_Delivery', 'Zero_Delivery', 'Customer_Count'].mean().round(1)
        trip_count = self.DF_Trip.groupby([target], as_index=False)['Actual_Delivery'].count()
        trip_sum = self.DF_Trip.groupby([target], as_index=False)['Actual_Delivery'].sum()

        DF1 = reduce(lambda left, right: pd.merge(left, right, on=[target]),[trip_avg, trip_count, trip_sum])
        DF1.columns = [target, 'Ø Del', 'Ø 0 Del', 'Customers','# Trips', 'Total Del']
        DF1['0 Del ()'] = (DF1['Ø 0 Del'] / DF1['Customers'] * 100).round(1)
        DF1.drop(['Ø 0 Del', 'Customers'], axis=1)
# ------------------------------------
        self.DF_TripHeader['Delivery_time'] = self.DF_TripHeader.apply(lambda row:(int(days_between(row.Trip_StartTime,row.Trip_EndTime))),axis=1)
        self.DF_TripHeader['Delivery_time'] = self.DF_TripHeader['Delivery_time'].fillna(0)
        DF2 = self.DF_TripHeader.groupby(['TH_Shop'], as_index=False)['Delivery_time'].mean().round(1)
        DF2['Ø Time'] = DF2.apply(lambda row: (convert_sec_to_time(row.Delivery_time)), axis=1)

        Output = DF1.merge(DF2, left_on=target, right_on='TH_Shop', how='left').drop('TH_Shop', axis=1)
        Output['Ø Del/h'] = ((Output['Ø Del'] / (Output['Delivery_time'])) * 3600).round(1)
        Output = Output.drop(['Delivery_time'], axis=1)
#-------------------------------------
        try:
            self.DF_CustomerAccounts = self.DF_CustomerAccounts.groupby(['CA_Shop'], as_index=False)['Open Invoices'].sum()
            Output = Output.merge(self.DF_CustomerAccounts, how='left', left_on=[target], right_on=['CA_Shop']).drop(['CA_Shop'], axis=1)
            Output['Open Invoices'] = Output['Open Invoices'].map(lambda x: "INR {0:,.0f}".format(x))
        except:
            pass
#----------------------------------------
        self.DF_CustomerMaster = self.DF_CustomerMaster.groupby(['CM_Shop'], as_index=False)['# New Customers'].sum()
        Output = Output.merge(self.DF_CustomerMaster, how='left', left_on=[target], right_on=['CM_Shop']).drop(['CM_Shop'], axis=1)
#------------------------------------
        self.DF_Complaints = self.DF_Complaints.groupby(['COM_Shop'], as_index=False)['Total Complaints', 'Closed Complaints'].sum()
        Output = Output.merge(self.DF_Complaints, how='left', left_on=[target], right_on=['COM_Shop']).drop(['COM_Shop'], axis=1)
        Output['% Closed'] = (Output['Closed Complaints']/Output['Total Complaints']*100).round(1)
        Output = Output.drop(['Closed Complaints'], axis=1)
#------------------------------
        Output = Output.fillna('')

        return Output
