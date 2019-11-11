import glob
import os
import pandas as pd
import numpy as np
import csv
from scipy.stats import ranksums
import matplotlib.pyplot as plt
import seaborn as sns
from reference import matched_gages
from Utils.calc_tabulate_wilcox import calc_tabulate_wilcox
from Utils.calc_metric_map import calc_metric_map
from Utils.calc_pdf import calc_pdf

class Gage:
    '''
    Organize all info on gage metrics and subsequent analysis
    '''
    # Initializer / Instance Attributes

    def __init__(self, name, metrics_file):
        self.name = name[:-19]
        # placeholder until I map out class references
        self.hyd_class = 2
        self.metrics_file = metrics_file
        self.summary_dict = None
        self.hist_flow = None
        self.fut_flow = None
        self.hist_vals = None
        self.fut_vals = None
        self.metrics_maps = None
        self.lat = None
        self.lon = None
        
    def wilcox_vals(self, metrics_file):
        # Uncomment line below to limit analysis to only select gages
        # if self.name not in matched_gages:
        #     return
        gage = []
        hyd_class = []
        metric = []
        hist_mean = []
        fut_mean = []
        wilcoxon_stat = []
        p_val = []

        loc_data = pd.read_csv('data/simulation_output/site_info.csv')
        for index, name in enumerate(loc_data['name']):
            if name == self.name:
                self.lat = loc_data['lat'][index]
                self.lon = loc_data['lon'][index]
                break

        wd = os.getcwd()
        try:
            os.mkdir(wd+'/data/vioplot/{}'.format(self.name))
            os.mkdir(wd+'/data/vioplot/{}/viodata'.format(self.name))
        except:
            pass
        for row in metrics_file.index:
            gage.append(self.name)
            hyd_class.append(self.hyd_class)
            vals = metrics_file.iloc[row]
            # historic range is from index #1 to index # 56 (1950-2005)
            # future range is from index #71 to index # 151 (2020-2099)
            metric_name = metrics_file.iloc[row][0]            
            drop_metrics =['SP_Tim','DS_Tim','DS_Dur_WSI','DS_No_Flow','FA_Tim','Wet_Tim','Peak_Tim_2_Water','Peak_Tim_5_Water','Peak_Tim_10','Peak_Tim_20','Peak_Tim_50','Peak_Tim_10_Water','Peak_Tim_20_Water','Peak_Tim_50_Water']
            if metric_name in drop_metrics:
                continue

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
            self.hist_vals = hist_vals
            self.fut_vals = fut_vals

            vals_df = pd.DataFrame({'hist':pd.Series(self.hist_vals), 'fut':pd.Series(self.fut_vals)})
            vals_df = vals_df[['hist', 'fut']]
            vals_df.to_csv(wd+'/data/vioplot/{}/viodata/{}.csv'.format(self.name, metric_name, index=False))
            
            statistic, p_value = ranksums(hist_vals, fut_vals)
            wilcoxon_stat.append(statistic)
            p_val.append(p_value)
            cols = ['Gage','Class','Metric', 'Hist_mean', 'Fut_mean', 'Wilcoxon_stat','p-val']
            df = pd.DataFrame(list(zip(gage, hyd_class, metric, hist_mean, fut_mean, wilcoxon_stat, p_val)),columns = cols)
            # if self.name in matched_gages: # uncomment if limiting analysis to specific gages
            df.to_csv(wd+'/data/stat_analysis_2/{}.csv'.format(self.name), index=None)
            self.wilcox = df
    
    def tabulate_wilcox(self):
        map_df = pd.DataFrame(columns=['name','lat','lon','Avg','Std','CV','Spring timing','Spring mag','Spring duration','Spring rate change','Dry season timing','Dry season mag 90p','Dry season mag 50p','Dry season duration','Fall pulse timing','Fall pulse mag','Wet season timing','Fall pulse duration','Wet season mag 10p','Wet season mag 50p','Wet season duration','Peak duration 10','Peak duration 20','Peak duration 50','Peak mag 10','Peak mag 20','Peak mag 50','Peak frequency 10','Peak frequency 20','Peak frequency 50'])
        summary_dict, metrics_mapping = calc_tabulate_wilcox()
        self.summary_dict = summary_dict
        self.metrics_maps = metrics_mapping
        vals = metrics_mapping[self.name]
        map_df = map_df.append({'name':self.name,'lat':self.lat, 'lon':self.lon,'Avg':vals[0],'Std':vals[1],'CV':vals[2],'Spring timing':vals[3],'Spring mag':vals[4],'Spring duration':vals[5],'Spring rate change':vals[6],'Dry season timing':vals[7],'Dry season mag 90p':vals[8],'Dry season mag 50p':vals[9],'Dry season duration':vals[10],'Fall pulse timing':vals[11],'Fall pulse mag':vals[12],'Wet season timing':vals[13],'Fall pulse duration':vals[14],'Wet season mag 10p':vals[15],'Wet season mag 50p':vals[16],'Wet season duration':vals[17],'Peak duration 10':vals[18],'Peak duration 20':vals[19],'Peak duration 50':vals[20],'Peak mag 10':vals[21],'Peak mag 20':vals[22],'Peak mag 50':vals[23],'Peak frequency 10':vals[24],'Peak frequency 20':vals[25],'Peak frequency 50':vals[26]},ignore_index=True)
        wd = os.getcwd()
        map_df.to_csv(wd+'/data/wilcoxon/indiv_results/{}.csv'.format(self.name), index=None)

    def pdf(self,flow_file):
        hist_flow, fut_flow = calc_pdf(self.name,flow_file)
        self.hist_flow = hist_flow
        self.fut_flow = fut_flow

def define_objects(metric_files,flow_files):
    for index, file in enumerate(metric_files):
        metrics_file = pd.read_csv(file, sep=',', index_col = None)
        metrics_name = file.split('/')[2][:-4]
        current_gage = Gage(metrics_name, metrics_file)
        # current_gage.wilcox_vals(metrics_file)
        # current_gage.tabulate_wilcox()
        for index, f_file in enumerate(flow_files):
            flow_file = pd.read_csv(f_file, sep=',', index_col = None)
            flow_name = f_file[27:-4]
            if flow_name == metrics_name[:-19]:
                current_gage.pdf(flow_file)

metric_files = glob.glob('data/ffc_metrics/*')
flow_files = glob.glob('data/simulation_output_cms/*')
result = define_objects(metric_files,flow_files)
# summary_dict = tabulate_wilcox()
