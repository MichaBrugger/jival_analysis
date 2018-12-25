import os

"""
Saving the output as a csv and html file for both a general overview and splitted for every shop.
The html output is for the managers in the water-shop, since its easily accessible, but can't be changed by them.
The csv output is generated for further analysis.
"""

class Save_Output:

    def __init__(self, date, df_final):

        self.date = date
        self.df_final = df_final

    def save_to_folder(self):

        # Getting a unique list of all the shops in the data
        Shop_List = self.df_final['TD_Shop'].unique()

        # Looping through the Shop_List, to create individual files/folders for every shop
        for Shop in range(len(Shop_List)):
            ShopName = Shop_List[Shop]
            if not os.path.exists('Output/' + Shop_List[Shop]):
                os.makedirs('Output/' + Shop_List[Shop])
            df_shop = (self.df_final.loc[self.df_final['TD_Shop']==ShopName])
            df_shop.to_csv('Output/' + ShopName + '/{}_{}.csv'.format(ShopName, self.date), index=False)
            df_shop.to_html('Output/' + ShopName + '/{}_{}.html'.format(ShopName, self.date), index=False, justify='left')

        # Saving a final overview in csv and html
        self.df_final.to_csv('Output/' + "Overview_{}.csv".format(self.date), index=False)
        self.df_final.to_html('Output/' + "Overview_{}.html".format(self.date), index=False, justify='left')