import pandas as pd
from functools import reduce

class Calc_Delivery:

    def __init__(self, DF_Trip):

        self.DF_Trip = DF_Trip

    def calc(self):

        # ad stands for Actual Delivery, pd stands for Planned Delivery and zero stands for Zero Delivery (Planned Delivery > 0 and Actual Delivery = 0)
        df_mean_ad = self.DF_Trip.groupby(['TD_Shop', 'TD_Route', 'TD_Driver'], as_index=False)['Actual_Delivery'].mean().round(1)
        df_mean_ad.columns = ['TD_Shop', 'TD_Route', 'TD_Driver', 'Ø Delivery']
        df_mean_customers = self.DF_Trip.groupby(['TD_Shop', 'TD_Route', 'TD_Driver'], as_index=False)['Customer_Count'].mean().round(1)
        df_mean_customers.columns = ['TD_Shop', 'TD_Route', 'TD_Driver', 'Ø Customer Count']
        df_mean_zero = self.DF_Trip.groupby(['TD_Shop', 'TD_Route', 'TD_Driver'], as_index=False)['Zero_Delivery'].mean().round(1)
        df_min = self.DF_Trip.groupby(['TD_Shop', 'TD_Route', 'TD_Driver'], as_index=False)['Actual_Delivery'].min()
        df_max = self.DF_Trip.groupby(['TD_Shop', 'TD_Route', 'TD_Driver'], as_index=False)['Actual_Delivery'].max()
        df_count = self.DF_Trip.groupby(['TD_Shop', 'TD_Route', 'TD_Driver'], as_index=False)['Actual_Delivery'].count()
        df_sum = self.DF_Trip.groupby(['TD_Shop', 'TD_Route', 'TD_Driver'], as_index=False)['Actual_Delivery'].sum()
        df_mean_pd = self.DF_Trip.groupby(['TD_Shop', 'TD_Route', 'TD_Driver'], as_index=False)['Planned_Delivery'].mean().round(1)

        # Establishing final delivery dataframe
        df_delivery = reduce(lambda left, right: pd.merge(left, right, on=['TD_Shop', 'TD_Route', 'TD_Driver']),
                          [df_count, df_sum, df_mean_zero, df_mean_ad, df_mean_pd, df_min, df_max, df_mean_customers])

        # Calculating the percentage average amount of 0 deliveries and adding it to final delivery dataframe
        # Done by taking the average amount of 0 deliveries divided by the average amount of customers for this route
        df_delivery['Ø 0 Delivery (%)'] = (df_delivery['Zero_Delivery']/df_delivery['Ø Customer Count']*100).round(1)

        # Naming columns properly
        df_delivery.columns = ['TD_Shop', 'TD_Route', 'TD_Driver', '# Trips', 'Total Deliveries', 'Ø 0 Delivery',
                               'Ø Delivery','Ø Planned', 'Min Delivery', 'Max Delivery','Ø Customer Count', 'Ø 0 Delivery (%)']

        # Dropping unneeded columns (Avg Customer Count, Avg 0 Delivery)
        # Decided to also drop some columns, that I might use later (Min Delivery, Max Delivery, Avg Planned) but I
        # still keep the calculation so I can easily put them back into the data frame if needed
        df_delivery = df_delivery.drop(['Ø Customer Count', 'Min Delivery', 'Max Delivery', 'Ø Planned',
                                        'Ø 0 Delivery'], axis=1)

        #returning data frame for all delivery-related values
        print('DF_Delivery created')
        return df_delivery
