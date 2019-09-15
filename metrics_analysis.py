import glob
import pandas as pd
import numpy as np
import csv
from scipy.stats import ranksums

class Gage:
    '''
    Organize all info on gage metrics and subsequent analysis
    '''
    # Initializer / Instance Attributes

    def __init__(self, name, metrics_file):
        self.name = name
        # placeholder until I map out class references
        self.hyd_class = 2
        self.metrics_file = metrics_file
        
    def wilcox_vals(self, metrics_file):
        gage = []
        hyd_class = []
        metric = []
        hist_mean = []
        fut_mean = []
        wilcoxon_stat = []
        p_val = []
        for row in metrics_file.index:
            gage.append(self.name)
            hyd_class.append(self.hyd_class)
            vals = metrics_file.iloc[row]
            # historic range is from index #1 to index # 56 (1950-2005)
            # future range is from index #71 to index # 151 (2020-2099)
            metric.append(vals[0])
            hist_vals = vals.iloc[1:57]
            hist_vals = hist_vals.to_numpy()
            for index, val in enumerate(hist_vals):
                try:
                    hist_vals[index] = float(val)
                except:
                    hist_vals[index] = np.nan
            hist_vals = hist_vals.astype(dtype=np.float64)
            hist_vals = np.array(hist_vals, dtype=np.float)
            hist_mean.append(np.nanmean(hist_vals))
            
            fut_vals = vals.iloc[71:151]
            fut_vals = fut_vals.to_numpy()
            for index, val in enumerate(fut_vals):
                try:
                    fut_vals[index] = float(val)
                except:
                    fut_vals[index] = np.nan
            fut_vals = fut_vals.astype(dtype=np.float64)
            fut_vals = np.array(fut_vals, dtype=np.float)
            fut_mean.append(np.nanmean(fut_vals))
            
            statistic, p_value = ranksums(hist_vals, fut_vals)
            wilcoxon_stat.append(statistic)
            p_val.append(p_value)

        cols = ['Gage','Class','Metric', 'Hist_mean', 'Fut_mean', 'Wilcoxon_stat','p-val']
        df = pd.DataFrame(list(zip(gage, hyd_class, metric, hist_mean, fut_mean, wilcoxon_stat, p_val)),columns = cols)
        # df.to_csv('data/stat_analysis/{}.csv'.format(self.name), index=None)
        self.wilcox = df
        
def define_objects(files):
    for index, file in enumerate(files):
        metrics_file = pd.read_csv(file, sep=',', index_col = None)
        name = file.split('/')[2][:-4]
        current_gage = Gage(name, metrics_file)
        current_gage.wilcox_vals(metrics_file)
        import pdb; pdb.set_trace()

files = glob.glob('data/ffc_metrics/*')
result = define_objects(files)
