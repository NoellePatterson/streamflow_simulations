import glob
import os
import pandas as pd
import numpy as np
import csv

wd = os.getcwd()
input_files = glob.glob(wd+'/data/wilcoxon/indiv_results/*.csv')

for index, file in enumerate(input_files):
    df = pd.read_csv(file, sep=',', index_col = None)
    if index == 0:
        final_df = df
    else:
        final_df = pd.concat([final_df,df],ignore_index = True)
final_df.to_csv(wd+'/data/wilcoxon/wilcoxon_all.csv',index=None)
import pdb; pdb.set_trace()