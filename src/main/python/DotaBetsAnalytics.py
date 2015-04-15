import networkx as nx
import matplotlib.pyplot as plt

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

    def analyze_graph(self, graph):
            edges = graph.edges()
            matches = [((1 - 1/graph[u][v]['matches']) * 1.5) for u, v in edges]
            nx.draw_networkx(graph, with_labels=False, node_size=50, width=matches, arrows=False, node_color='green', edge_color='orange')
            plt.show()

