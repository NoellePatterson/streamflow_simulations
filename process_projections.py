# Analyze dataset of 20 hydrologic simulations at 59 sites in northern CA
# Pull date and flow columns into FFC-readable csv format
# Pull general site metadata into mappable format
# Pull specific time periods into historic/future plotting format

import glob
import pandas as pd
import xarray as xr
from datetime import datetime
import numpy as np
import csv
from collections import OrderedDict
import itertools
import re

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
		flow = flow.tolist()
		dct = {'date':dates, 'flow':flow_cfs[0:-1]} # remove weird final val from flows col
		flow_output = pd.DataFrame(data = dct) 
		name = df['outlet_name'][0][index].iloc[0].decode('ASCII')
		flow_output.to_csv('data/simulation_output/' + name + '.csv', sep=',', index=False)
		# csm flow output
		dct_cms = {'date':dates, 'flow':flow[0:-1]} # remove weird final val from flows col
		flow_output_cms = pd.DataFrame(data = dct_cms) 
		flow_output_cms.to_csv('data/simulation_output_cms/' + name + '.csv', sep=',', index=False)

def get_site_info(files):
	file = files[0] # for now just use the first file, which is one of the many modelling/routing scenarios
	site_info_dct = {'name':[], 'lat':[], 'lon':[]}
	dataset = xr.open_dataset(file)
	df = dataset.to_dataframe()
	sites = np.unique(df['outlet_name'])
	import pdb; pdb.set_trace()
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

	site_info_df.to_csv('data/simulation_output/site_info.csv', sep=',', index=False)

def create_plotters(files):
	# create csv outputs of specific years to feed into dim hydro plotter
	file = files[0] # for now just use the first file, which is one of the many modelling/routing scenarios
	dates = []
	dataset = xr.open_dataset(file)
	df = dataset.to_dataframe()
	dates = dates[0:-1]
	time = df['time_bnds'][0][0] # beware of multi level indexing
	for index in time:
		date_gregorian = index
		date = date_gregorian.strftime("%m/%d/%Y")
		dates.append(date)
	# Set beginning and end of plotting periods
	for index, date in enumerate(dates):
		if date == '12/31/2015':
			hist_end = index
			continue
		if date == '01/01/2035':
			fut_beg = index
			continue
	dates_hist = dates[0:hist_end]
	dates_fut = dates[fut_beg:len(dates)-1]

	hist_flow_agg = [np.nan] * len(dates_hist)
	fut_flow_agg = [np.nan] * len(dates_fut)
		
	num_sites = len(np.unique(df['outlet_name']))
	for index in range(num_sites): # iterate over all 59 sites
		name = df['outlet_name'][0][index].iloc[0].decode('ASCII')
		flow = df['streamflow'][0][index].iloc[0:-1] # remove zero flow day at end of all projections
		flow_cfs = (flow * 35.314666212661).tolist()
		flow_hist = flow_cfs[0:hist_end]
		flow_fut = flow_cfs[fut_beg:len(flow_cfs)+1]
		plot_outputs = OrderedDict()
		new_name = re.sub('\D', '', name)
		plot_outputs['result_dt_hist'] = dates_hist
		plot_outputs[new_name+'1'] = flow_hist
		plot_outputs['result_dt_fut'] = dates_fut
		plot_outputs[new_name+'2'] = flow_fut

		# add values to aggregate lists
		for i, val in enumerate(flow_hist):
			if index == 0:
				hist_flow_agg[i] = [val]
			else:
				hist_flow_agg[i].append(val)
		for i, val in enumerate(flow_fut):
			if index == 0:
				fut_flow_agg[i] = [val]
			else:
				fut_flow_agg[i].append(val)

		# write results to csv format
		class_row = ['',10,'',11]
		csv_columns = plot_outputs.keys()
		csv_file = 'data/plotter/'+ name +'.csv'
		keys = plot_outputs.keys()
		# import pdb; pdb.set_trace()
		try:
			with open(csv_file, 'w') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerow(class_row)
				writer.writerow(keys)
				writer.writerows(itertools.izip_longest(*[plot_outputs[key] for key in keys]))
		except IOError:
			print("I/O error") 

	# print aggregate lists
	agg_outputs = OrderedDict()
	for index, value in enumerate(hist_flow_agg):
		hist_flow_agg[index] = np.nanmean(value)
	for index, value in enumerate(fut_flow_agg):
		fut_flow_agg[index] = np.nanmean(value)
	agg_outputs['result_dt_hist'] = dates_hist
	agg_outputs['agg_flow_hist'] = hist_flow_agg
	agg_outputs['result_dt_fut'] = dates_fut
	agg_outputs['agg_flow_fut'] = fut_flow_agg

	csv_file = 'data/plotter/aggregate.csv'
	keys = agg_outputs.keys()
	try:
		with open(csv_file, 'w') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(['',2,'',2])
			writer.writerow(keys)
			writer.writerows(itertools.izip_longest(*[agg_outputs[key] for key in keys]))
	except IOError:
		print("I/O error") 

files = glob.glob('data/simulations/*')
# create_plotters(files)
# site = get_site_info(files)
# csv = create_csvs(files)
