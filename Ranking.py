import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import HTML

class Ranking:

    def __init__(self, Output_Raw):

        self.Output_Raw = Output_Raw

    def rank(self, target):

        Output_Ranked = self.Output_Raw[target + ['Ø Del', 'Complaints', '# New Customers']].copy()
        Output_Ranked['Rank'] = Output_Ranked['Ø Del'].rank(ascending=False)
        Output_Ranked = Output_Ranked.sort_values(['Rank'])

        # Set colormap equal to seaborns light green color palette
        cm = sns.light_palette("green", as_cmap=True)

        (Output_Ranked.style
         .background_gradient(cmap=cm, subset=['Rank'])
         .highlight_max(subset=['Rank'])
         .set_caption('This is a custom caption.')
         .format({'Rank': "{:.0f%}"})
         .set_table_styles(styles))

        return Output_Ranked