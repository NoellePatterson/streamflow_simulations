import glob
import pandas as pd
import xarray as xr
from datetime import datetime
import numpy as np



def get_date_col(file):
    dates = []
    dataset = xr.open_dataset(file)
    df = dataset.to_dataframe()
    time = df['time_bnds'][0][0] # beware of multi level indexing
    for index in time:
        date_gregorian = index
        date = date_gregorian.strftime("%m/%d/%Y")
        dates.append(date)
    dates = dates[0:-1] # last val looks weird so remove it
    return dates

def create_csvs(files):
	file = files[0] # for now just use the first file, which is one of the many modelling/routing scenarios
	dates = get_date_col(file)
	dct = {}
	dataset = xr.open_dataset(file)
	df = dataset.to_dataframe()
	sites = np.unique(df['outlet_name'])
	for index, site in enumerate(sites):	
		flow = df['streamflow'][0][index]
		flow_cfs = (flow * 35.314666212661).tolist()
		dct = {'date':dates, 'flow':flow_cfs[0:-1]} # remove weird final val from flows col
		flow_output = pd.DataFrame(data = dct) 
		name = df['outlet_name'][0][index].iloc[0].decode('ASCII')
		# import pdb; pdb.set_trace()
		flow_output.to_csv('data_output/' + name + '.csv', sep=',', index=False)

def get_site_info(files):
	file = files[0] # for now just use the first file, which is one of the many modelling/routing scenarios
	site_info_dct = {'name':[], 'lat':[], 'lon':[]}
	dataset = xr.open_dataset(file)
	df = dataset.to_dataframe()
	sites = np.unique(df['outlet_name'])
	for index in range(len(sites)):
		# site_info_dt[site.decode('ASCII')] = df[loc]
		name = df['outlet_name'][0][index].iloc[0].decode('ASCII')
		lon = df['lon'][0][index].iloc[0]
		lat = df['lat'][0][index].iloc[0]
		site_info_dct['name'].append(name)
		site_info_dct['lat'].append(lat)
		site_info_dct['lon'].append(lon)

	[dict(zip(site_info_dct, col)) for col in zip(*site_info_dct.values())]
	site_info_df = pd.DataFrame.from_dict(site_info_dct)

	site_info_df.to_csv('data_output/site_info.csv', sep=',', index=False)
        
files = glob.glob('data/*')
# site = get_site_info(files)
# csv = create_csvs(files)
