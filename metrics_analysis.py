import glob
import os
import pandas as pd
import numpy as np
import csv
from scipy.stats import ranksums
import matplotlib.pyplot as plt
import seaborn as sns
from reference import matched_gages

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
        self.hist_vals = None
        self.fut_vals = None
        
    def wilcox_vals(self, metrics_file):
        if self.name not in matched_gages:
            return
        gage = []
        hyd_class = []
        metric = []
        hist_mean = []
        fut_mean = []
        wilcoxon_stat = []
        p_val = []

        wd = os.getcwd()
        try:
            os.mkdir(wd+'/data/vioplot/{}'.format(self.name))
            os.mkdir(wd+'/data/vioplot/{}/viodata'.format(self.name))
        except:
            print('folder already exists')
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
            if self.name in matched_gages:
                df.to_csv(wd+'/data/stat_analysis_2/{}.csv'.format(self.name), index=None)
            self.wilcox = df

    def violins(self):
        '''
        Plot violin plots of historic and future values
        '''
        # organize both lists into single long format
        hist_df = pd.DataFrame(self.hist_vals)
        plot_data  = pd.DataFrame({'hist':pd.Series(self.hist_vals), 'fut':pd.Series(self.fut_vals)})
        melt = pd.melt(plot_data)

        ax = plt.subplot()
        import pdb; pdb.set_trace()
        ax = sns.violinplot(melt, showmedians=True)
        import pdb; pdb.set_trace()
        ax = sns.violinplot(self.hist_vals, showmedians=True)
        ax = sns.violinplot(self.fut_vals, showmedians=True)
        plt.show()
        # still struggling... can't figure out how to plot both items independently, different lengths creating issues. May fall back on R violin plot code. 
        

def tabulate_wilcox():
    summary_dict = {}
    wilcox_files = glob.glob('data/stat_analysis_2/*')
    # loop through each gage file
    for index, file in enumerate(wilcox_files):
        wilcox = pd.read_csv(file, sep=',', index_col = None)
        # Create empty lists (pos and neg categories) to fill up for each metric in file, only do this once
        if index == 0:
            for i, metric in enumerate(wilcox['Metric']):
                summary_dict[metric] = {}
                summary_dict[metric]['pos'] = []
                summary_dict[metric]['neg'] = []
        for i, metric in enumerate(wilcox['Metric']):
            if wilcox['p-val'][i] < 0.05 and wilcox['Wilcoxon_stat'][i] > 0:
                summary_dict[metric]['pos'].append(1)
            elif wilcox['p-val'][i] < 0.05 and wilcox['Wilcoxon_stat'][i] < 0:
                summary_dict[metric]['neg'].append(1)

    df = pd.DataFrame.from_dict(summary_dict, orient='index')
    for i, metric in enumerate(wilcox['Metric']):
        df['pos'][metric] = sum(df['pos'][metric])/float(13)*100
        df['neg'][metric] = sum(df['neg'][metric])/float(13)*100

ax = df.plot.bar(figsize=(10, 7), legend=True, fontsize=10, color = ('blue','red'))
    plt.margins(0.2)
    plt.subplots_adjust(bottom=0.2)
    plt.title('Wilcoxon Significant Differences')
    plt.ylabel('Percent significance of matching sites')
    L=plt.legend()
    L.get_texts()[0].set_text('Positive change')
    L.get_texts()[1].set_text('Negative change')
    df.to_csv('data/wilcoxon_summary.csv')
    fig=ax.get_figure()
    fig.savefig('data/wilcoxon_summary.png')
    return summary_dict

def define_objects(files):
    for index, file in enumerate(files):
        metrics_file = pd.read_csv(file, sep=',', index_col = None)
        name = file.split('/')[2][:-4]
        current_gage = Gage(name, metrics_file)
        current_gage.wilcox_vals(metrics_file)
        # current_gage.violins()

files = glob.glob('data/ffc_metrics/*')
result = define_objects(files)
summary_dict = tabulate_wilcox()
