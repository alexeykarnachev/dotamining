class DotaBetsAnalytics:
    def __init__(self):
        pass

    def count_ev(self, winrate, coeff):
        return (winrate * coeff) - (1-winrate) * 1

    def count_marginal_p(self, results):

        return sum(results)/len(results)

