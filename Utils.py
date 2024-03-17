#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 17:50:47 2024

@author: michaelcauson
"""

# Imports
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

# Elo class will have abstract methods to be filled by the particular rating system
class Elo:
    
    def __init__(self,start_season,
                 initial_elo,K):
        self.start_season = start_season
        self.initial_elo = initial_elo
        self.K = 32
        self.std_start = 100
        self.std_reduction_factor = 1
        self.current_season = start_season
        self.season_data = self.read_season(season_string=start_season)
        self.elo_table = self.initialise_elo_table(start_season=self.start_season)

    # Grab any single season's data
    def read_season(self,season_string='9_10'):
        
        df = pd.read_csv('Data/' + season_string + '.csv',encoding='utf8')    
        df = df[["Date",
                 "HomeTeam","AwayTeam",
                 "FTHG","FTAG","FTR",
                 "B365H","B365D","B365A"]]
        df['HomeElo'] = np.zeros(len(df['Date']))
        df['AwayElo'] = np.zeros(len(df['Date']))
        df['HomeStd'] = np.zeros(len(df['Date']))
        df['AwayStd'] = np.zeros(len(df['Date']))
        return df
    
    # Create initial Elo table (start point)
    def initialise_elo_table(self,start_season='9_10'):
        
        df_start = self.read_season(season_string = start_season)
        team_list = sorted(df_start['HomeTeam'].unique())
        gp_list = np.zeros_like(team_list, dtype=int)
        elo_list = np.ones_like(team_list, dtype=float) * self.initial_elo
        elo_std_list = np.ones_like(team_list, dtype=float) * self.std_start
        return pd.DataFrame({'Team': team_list, 'Games Played': gp_list,
                             'Elo': elo_list, 'Elo_std': elo_std_list})
    
    # Sweeps through the current season's data with rating system
    def sweep_season(self):
        
        for i in range(len(self.season_data)):
            home_team = self.season_data.iloc[i]['HomeTeam']
            away_team = self.season_data.iloc[i]['AwayTeam']
            
            home_elo = float(self.elo_table[self.elo_table['Team'] == home_team]['Elo'].iloc[0])
            away_elo = float(self.elo_table[self.elo_table['Team'] == away_team]['Elo'].iloc[0])
            
            home_id = self.elo_table.loc[self.elo_table['Team'] == home_team].index.tolist()[0]
            away_id = self.elo_table.loc[self.elo_table['Team'] == away_team].index.tolist()[0]
            
            home_elo_std = self.elo_table.iloc[home_id,3]
            away_elo_std = self.elo_table.iloc[away_id,3]
            
            std_max = np.maximum(home_elo_std,away_elo_std)
         
            self.season_data.iloc[i,self.season_data.columns.get_loc("HomeElo")] = home_elo
            self.season_data.iloc[i,self.season_data.columns.get_loc("AwayElo")] = away_elo
            self.season_data.iloc[i,self.season_data.columns.get_loc("HomeStd")] = home_elo_std
            self.season_data.iloc[i,self.season_data.columns.get_loc("AwayStd")] = away_elo_std
            
            expected_outcome = self.expected_outcome(home_elo, away_elo)
            if self.season_data.iloc[i]['FTHG'] > self.season_data.iloc[i]['FTAG']:
                true_outcome = 1
            elif self.season_data.iloc[i]['FTHG'] < self.season_data.iloc[i]['FTAG']:
                true_outcome = 0
            else:
                true_outcome = 0.5
                
            d_elo = self.update_elo(expected_outcome,true_outcome,std_max)
            
            new_home_elo = home_elo + d_elo
            new_away_elo = away_elo - d_elo
            
            self.elo_table.iloc[home_id,1] += 1
            self.elo_table.iloc[away_id,1] += 1
            self.elo_table.iloc[home_id,2] = new_home_elo
            self.elo_table.iloc[away_id,2] = new_away_elo
            self.elo_table.iloc[home_id,3] -= self.std_reduction_factor
            self.elo_table.iloc[away_id,3] -= self.std_reduction_factor
            
    # Deals with promotion/relegation
    def season_end(self):
        data_label = self.current_season.split("_")
        pass
    
    # Assign a win probability to home team
    @abstractmethod
    def expected_outcome(self,elo_home,elo_away):
        pass
    
    # Define increment to update ratings
    @abstractmethod
    def update_elo(self,expected_outcome,true_outcome,*args):
        pass
    

# Classic Elo rating system (Elo, 1967)
class Classic(Elo):
    
    def expected_outcome(self,elo_home,elo_away):
        return 1/(1+10**(-(elo_home-elo_away)/400))
    
    def update_elo(self,expected_outcome,true_outcome,std_max=None):
        
        return self.K * (true_outcome - expected_outcome)

# Glicko rating system (in peogress)
class Glicko(Elo):
    
    def expected_outcome(self,elo_home,elo_away):
        pass
    
    def update_elo(self,expected_outcome,true_outcome,std_max=None):
        pass

# Bayesian perpsective to Elo rating system (Ingram, 2021)
class Bayesian(Elo):
    
    def inv_logit(self,x):
        return np.exp(x) / (1 + np.exp(x))
        
    def expected_outcome(self,elo_home,elo_away):
        return self.inv_logit( (np.log(10)/400) * (elo_home-elo_away))
        
    
    def update_elo(self,expected_outcome,true_outcome,std_max):
        b = np.log(10)/400
        k = (b/2)/( (1/(2*std_max**2)) + b**2 * expected_outcome * (1-expected_outcome) )
        return k * (true_outcome - expected_outcome)


    






























    