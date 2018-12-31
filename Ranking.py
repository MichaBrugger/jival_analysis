class Ranking:

    def __init__(self, Output_Raw):

        self.Output_Raw = Output_Raw

    def rank(self, target, betterScore, Bonus):

        # Creating Output_Ranked and rank its individual scores (percentile)
        try:
            Output_Ranked = self.Output_Raw[target + ['Ø Del', 'Complaints', 'New Customers', 'Collected (%)']].copy()
            Output_Ranked['R_Rec'] = Output_Ranked['Collected (%)'].rank(ascending=False, pct=True)
        except:
            Output_Ranked = self.Output_Raw[target + ['Ø Del', 'Complaints', 'New Customers', 'Receipts']].copy()
            Output_Ranked['R_Rec'] = Output_Ranked['Receipts'].rank(ascending=False, pct=True)

        Output_Ranked['R_Del'] = Output_Ranked['Ø Del'].rank(ascending=False, pct=True)
        Output_Ranked['R_Com'] = Output_Ranked['Complaints'].rank(ascending=True, pct=True)
        Output_Ranked['R_New'] = Output_Ranked['New Customers'].rank(ascending=False, pct=True)

        # Calculating the individual overall score
        # BetterScore = You have to score better than X% of your peers (scaled from 0 to 1)
        # Logic: (betterScore * amount of disciplines) - sum percentage ranking for each discipline
        # The best possible score in each discipline is 0.0, the worst is 1)
        Output_Ranked['Score'] = (betterScore*4) - Output_Ranked[['R_Del', 'R_Com', 'R_New', 'R_Rec']].sum(axis=1)

        #Setting all scores below 0 to 0
        Output_Ranked['Score'] = Output_Ranked['Score'].clip(lower=0)

        #Calculate TotalScore to later calculate percentage of bonus share, then format Bonus as currency
        TotalScores = Output_Ranked['Score'].sum(axis=0)
        Output_Ranked['Bonus'] = (Output_Ranked['Score']/TotalScores*Bonus).round(-2)
        Output_Ranked['Bonus'] = Output_Ranked['Bonus'].map(lambda x: "INR {0:,.0f}".format(x))

        # Sort Output_Ranked according to Score
        Output_Ranked = Output_Ranked.sort_values(['Score'], ascending=False).reset_index(drop=True)

        # Basic formatting and returning Output_Ranked to Main
        try:
            Output_Ranked = Output_Ranked[target + ['Ø Del', 'Complaints', 'New Customers', 'Collected (%)', 'Bonus']]
        except:
            Output_Ranked = Output_Ranked[target + ['Ø Del', 'Complaints', 'New Customers', 'Receipts', 'Bonus']]

        print('Output_Ranked created')
        return Output_Ranked