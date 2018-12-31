import os

"""
Saving the output as a csv and html file for both a general overview and splitted for every shop.
The html output is for the managers in the water-shop, since its easily accessible, but can't be changed by them.
The csv output is generated for further analysis.
"""

class Save_Output:

    def __init__(self, dateToday, Output_Raw, Output_Ranked):

        self.dateToday = dateToday
        self.Output_Raw = Output_Raw
        self.Output_Ranked = Output_Ranked

    def save_to_folder(self):

        # Getting a unique list of all the shops in the data

        Shop_List = self.Output_Raw['Shop'].unique()

        # Looping through the Shop_List, to create individual files/folders for every shop
        for Shop in range(len(Shop_List)):
            ShopName = Shop_List[Shop]
            if not os.path.exists('Output/' + Shop_List[Shop]):
                os.makedirs('Output/' + Shop_List[Shop])
            df_shop = (self.Output_Raw.loc[self.Output_Raw['Shop']==ShopName])
            df_shop.to_csv('Output/' + ShopName + '/{}_{}.csv'.format(ShopName, self.dateToday), index=False)
            df_shop.to_html('Output/' + ShopName + '/{}_{}.html'.format(ShopName, self.dateToday), index=False, justify='left')


        # Saving a final overview in csv and html
        self.Output_Raw.to_csv('Output/' + "Overview_{}.csv".format(self.dateToday), index=False)
        self.Output_Ranked.to_csv('Output/' + "Ranked_{}.csv".format(self.dateToday), index=False)
        self.Output_Raw.to_html('Output/' + "Overview_{}.html".format(self.dateToday), index=False, justify='left')
        self.Output_Ranked.to_html('Output/' + "Ranked_{}.html".format(self.dateToday), index=False, justify='left')