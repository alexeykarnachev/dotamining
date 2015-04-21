import networkx as nx
import matplotlib.pyplot as plt


class DotaBetsAnalytics:
    """
    Class with analytics methods.
    """

    def __init__(self, graph: nx.DiGraph=None):
        self.graph = graph
        self.matches_matrix = nx.adjacency_matrix(graph, weight='matches')
        self.winrate_matrix = nx.adjacency_matrix(graph, weight='weight')
        self.teams = graph.nodes()

    def marginal_winrate(self, teams):
        marginal_winrate = []
        for team in teams:
            team_matches = self.matches_matrix[:, self.teams.index(team)].toarray()
            team_loserates = self.winrate_matrix[:, self.teams.index(team)].toarray()
            marginal_winrate.append(1 - float(sum(team_matches * team_loserates) / sum(team_matches)))

        return marginal_winrate

    def joint_winrate(self, teams):
        joint_winrate = 1 - self.winrate_matrix[self.teams.index(teams[1]), self.teams.index(teams[0])]

        return [joint_winrate, 1 - joint_winrate]

    def neighbors_winrate(self, teams):
        joint_neighbors = list(set(self.graph.neighbors(teams[0])) & set(self.graph.neighbors(teams[1])))
        joint_neighbors = [self.teams.index(i) for i in joint_neighbors]

        team_neighbors_winrate = []
        for team in teams:
            team_matches = self.matches_matrix[joint_neighbors, self.teams.index(team)].toarray()
            team_loserates = self.winrate_matrix[joint_neighbors, self.teams.index(team)].toarray()
            team_neighbors_winrate.append(1 - float(sum(team_matches * team_loserates) / sum(team_matches)))

        return team_neighbors_winrate





