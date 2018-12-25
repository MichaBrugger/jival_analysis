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

class Calc_Time:

    def __init__(self, DF_TripHeader):

        self.DF_TripHeader = DF_TripHeader

    def calc(self):
        # apply function to calculate delivery time for calculating average delivery time
        # fill missing values with 0, so I dont run into an error if a trip is still ongoing and has no end-time yet
        self.DF_TripHeader['Delivery_time'] = self.DF_TripHeader.apply(lambda row: (int(days_between(row.Trip_StartTime, row.Trip_EndTime))), axis=1)
        self.DF_TripHeader['Delivery_time'] = self.DF_TripHeader['Delivery_time'].fillna(0)

        # Calculating average delivery time per route/driver
        df_time = self.DF_TripHeader.groupby(['TH_Shop', 'TH_Route', 'TH_Driver'], as_index=False)['Delivery_time'].mean().round(1)
        df_time['Ø Time (h:m)'] = df_time.apply(lambda row: (convert_sec_to_time(row.Delivery_time)), axis=1)

        #returning dataframe for all time-related values
        return df_time