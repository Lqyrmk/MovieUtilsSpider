"""
:Description: 
:Author: lym
:Date: 2023/05/23/3:02
:Version: 1.0
"""
import pandas as pd
movie_data = pd.read_csv('movie.csv', low_memory=False)
print(len(movie_data))
