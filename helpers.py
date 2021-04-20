import glob
import numpy as np
import pandas as pd

sp_files = glob.glob('data/ffc_metrics/sp_tim/*.csv')
dry_files = glob.glob('data/ffc_metrics/dry_tim/*.csv')
wet_files = glob.glob('data/ffc_metrics/wet_tim/*.csv')

sp_tim = []
dry_tim = []
wet_tim = []

for file in sp_files:
    sp = pd.read_csv(file, header=None)
    sp_tim.append(sp.values.tolist())
for file in dry_files:
    dry = pd.read_csv(file, header=None)
    dry_tim.append(dry.values.tolist())
for file in wet_files:
    wet = pd.read_csv(file, header=None)
    wet_tim.append(wet.values.tolist())

sp_all_vals = [item[0] for sublist in sp_tim for item in sublist]
dry_all_vals = [item[0] for sublist in dry_tim for item in sublist]
wet_all_vals = [item[0] for sublist in wet_tim for item in sublist]

sp_mean = np.nanmean(sp_all_vals)
dry_mean = np.nanmean(dry_all_vals)
wet_mean = np.nanmean(wet_all_vals)
import pdb; pdb.set_trace()