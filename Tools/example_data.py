import pandas as pd

data = pd.read_csv('./Project/Dash/Tools/bikeshare_nyc_raw.csv', delimiter='\t')
data = data.drop_duplicates(subset=["dock_id"])
data = data.loc[data['in_service'] == 1,:]

keep = data.loc[:, ['dock_id','dock_name','_lat','_long']]

keep.to_csv('./Project/Dash/Tools/bikeshare_nyc_stations.csv')


test = 1