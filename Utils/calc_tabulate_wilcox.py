import glob
import os
import pandas as pd
import numpy as np
import csv
from scipy.stats import ranksums
import matplotlib.pyplot as plt
import seaborn as sns
from reference import matched_gages

def calc_tabulate_wilcox():
    summary_dict = {}
    metrics_mapping = {}
    wilcox_files = glob.glob('data/stat_analysis_2/*')
    # loop through each gage file
    for index, file in enumerate(wilcox_files):
        wilcox = pd.read_csv(file, sep=',', index_col = None)
        name = file[21:-4]
        metrics_mapping[name] = []
        # import pdb; pdb.set_trace()
        # Create empty lists (pos and neg categories) to fill up for each metric in file, only do this once
        if index == 0:
            for i, metric in enumerate(wilcox['Metric']):
                summary_dict[metric] = {}
                summary_dict[metric]['pos'] = []
                summary_dict[metric]['neg'] = []

        # Beware, Wilcoxon value is positive for a decrease between hist->fut, and is negative for increase from hist->fut
        for i, metric in enumerate(wilcox['Metric']):
            if wilcox['p-val'][i] < 0.05 and wilcox['Wilcoxon_stat'][i] > 0:
                summary_dict[metric]['pos'].append(1)
                metrics_mapping[name].append('dec')
            elif wilcox['p-val'][i] < 0.05 and wilcox['Wilcoxon_stat'][i] < 0:
                summary_dict[metric]['neg'].append(1)
                metrics_mapping[name].append('inc')
            else:
                metrics_mapping[name].append('none')

    df = pd.DataFrame.from_dict(summary_dict, orient='index')
    for i, metric in enumerate(wilcox['Metric']):
        gage_count = len(wilcox_files)
        df['pos'][metric] = sum(df['pos'][metric])/float(gage_count)*100
        df['neg'][metric] = sum(df['neg'][metric])/float(gage_count)*100

    # Set new df index names for plotting
    df = df.drop('Std')
    names = ['Average','Coefficient of variation','Dry season duration','Dry season mag. (50p)','Dry season mag. (90p)','Dry season timing','Fall pulse duration','Fall pulse mag.','Fall pulse timing','Peak mag. (10p)','Peak mag. (20p)','Peak mag. (50p)','Peak duration (10p)','Peak duration (20p)','Peak duration (50p)','Peak frequency (10p)','Peak frequency (20p)','Peak frequency (50p)','Spring rec. duration','Spring rec. mag.','Spring rec. rate of change','Spring rec. timing','Wet season duration','Wet season mag. (10p)','Wet season mag. (50p)','Wet season timing']
    df.index = names
    ax = df.plot.bar(figsize=(10, 10), legend=True, fontsize=10, color = ('blue','red'))
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
    plt.close()

    return summary_dict, metrics_mapping