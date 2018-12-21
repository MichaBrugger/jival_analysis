import os

class Save_Output:

    def __init__(self, date, df_final):

        self.date = date
        self.df_final = df_final

    def Save_to_Folder(self):

        # Getting a unique list of all the shops in the data
        Shop_List = self.df_final['Shop'].unique()

        # Looping through the Shop_List, to create individual files/folders for every shop
        for Shop in range(len(Shop_List)):
            ShopName = Shop_List[Shop]
            df_shop=[]
            if not os.path.exists('Output/' + Shop_List[Shop]):
                os.makedirs('Output/' + Shop_List[Shop])
            df_shop = (self.df_final.loc[self.df_final['Shop']==ShopName])
            df_shop.to_csv('Output/' + ShopName + '/{}_{}.csv'.format(ShopName, self.date), index=False)
            df_shop.to_html('Output/' + ShopName + '/{}_{}.html'.format(ShopName, self.date), index=False)

        # Saving a final overview in csv and html
        self.df_final.to_csv('Output/' + "Overview_{}.csv".format(self.date), index=False)
        self.df_final.to_html('Output/' + "Overview_{}.html".format(self.date), index=False)