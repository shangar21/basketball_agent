import pandas as pd

class Player():
    def __init__(self, dataframe, start_position):
        self.data = dataframe
        self.position = start_position

    def __init__(self, dataframe, player_name, start_position, name_column='name'):
        self.name = player_name
        self.data = dataframe[dataframe[name_column] == player_name]
        self.position = start_position

    def get_stat(self, stat_name):
        return self.data[stat_name].iloc[0]
