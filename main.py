#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 17:27:27 2024

@author: michaelcauson
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from Utils import *

elo = Classic("9_10",1500,32)
elo.sweep_season()
chelsea_data_classic = elo.season_data[(elo.season_data['HomeTeam'] == "Chelsea")]


bayes = Bayesian("9_10",1500,32,)
bayes.sweep_season()
chelsea_data_bayesian = bayes.season_data[(bayes.season_data['HomeTeam'] == "Chelsea")]

plt.figure(figsize=(20,5))
plt.plot(chelsea_data_classic['Date'],chelsea_data_classic['HomeElo'])
plt.plot(chelsea_data_bayesian['Date'],chelsea_data_bayesian['HomeElo'])
plt.plot(chelsea_data_bayesian['Date'],chelsea_data_bayesian['HomeElo'] + 2*np.sqrt(80),linestyle="--",color="black")
plt.plot(chelsea_data_bayesian['Date'],chelsea_data_bayesian['HomeElo'] - 2*np.sqrt(80),linestyle="--",color="black")