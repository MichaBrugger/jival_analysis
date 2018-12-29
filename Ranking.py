class Ranking:

    def __init__(self, Output_Raw):

        self.Output_Raw = Output_Raw

    def rank(self, target):

        Output_Ranked = self.Output_Raw[target + ['Ø Del', 'Complaints', '# New Customers']].copy()
        Output_Ranked['Rank'] = Output_Ranked['Ø Del'].rank(ascending=False)
        Output_Ranked = Output_Ranked.sort_values(['Rank'])

        return Output_Ranked