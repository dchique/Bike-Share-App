import pandas as pd

c1 = pd.read_csv('./Tools/cluster 1 predictions.csv')
c2 = pd.read_csv('./Tools/cluster_2_prediction.csv')
c3 = pd.read_csv('./Tools/cluster3_prediction.csv')
c4 = pd.read_csv('./Tools/cluster 4 predictions.csv')

combined = pd.concat([c1,c2,c3,c4], ignore_index=True)
combined.to_csv('./Tools/all_predictions.csv')
