import networkx as nx
import matplotlib.pyplot as plt


class DotaBetsAnalytics:
    """
    Class with analytics methods.
    """

    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
        self.matches_matrix = nx.adjacency_matrix(graph, weight='matches')
        self.winrate_matrix = nx.adjacency_matrix(graph, weight='weight')
        self.teams = graph.nodes()

    def count_ev(self, winrate, coeff):
        """
        Method for counting expected value within the winrate and coefficient.
        """
        return (winrate * coeff) - (1 - winrate) * 1

    def marginal_winrate(self, team):
        team_matches = self.matches_matrix[:, self.teams.index(team)].toarray()
        team_loserates = self.winrate_matrix[:, self.teams.index(team)].toarray()
        marginal_winrate = 1 - float(sum(team_matches * team_loserates) / sum(team_matches))

        return marginal_winrate

    def joint_winrate(self, team, opponent):
        joint_winrate = 1 - self.winrate_matrix[self.teams.index(opponent), self.teams.index(team)]

        return joint_winrate

    def joint_neighbors_winrate(self, team, opponent):
        joint_neighbors = list(set(self.graph.neighbors(team)) & set(self.graph.neighbors(opponent)))
        joint_neighbors = [self.teams.index(i) for i in joint_neighbors]

        team_matches = self.matches_matrix[joint_neighbors, self.teams.index(team)].toarray()
        team_loserates = self.winrate_matrix[joint_neighbors, self.teams.index(team)].toarray()
        team_neighbors_winrate = 1 - float(sum(team_matches * team_loserates) / sum(team_matches))

        return team_neighbors_winrate

