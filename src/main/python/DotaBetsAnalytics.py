class DotaBetsAnalytics:
    """
    Class with analytics methods.
    """
    def __init__(self):
        pass

    def count_ev(self, winrate, coeff):
        """
        Method for counting expected value within the winrate and coefficient.
        """
        return (winrate * coeff) - (1-winrate) * 1

    def count_p(self, results):
        """
        Method for counting winrate from binary results vector.
        """
        return sum(results)/len(results)

