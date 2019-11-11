import glob
import os
import pandas as pd
import numpy as np
import scipy
import matplotlib.pyplot as plt
import seaborn as sns
import csv

def calc_pdf(name,flow_file):
    hist_flow = flow_file['flow'][0:20453]
    fut_flow = flow_file['flow'][25567:54786]

    fig2 = plt.figure(2,figsize=(13,5))
    ax2 = fig2.gca()
    ax2 = sns.distplot(hist_flow, hist=False, kde=True, label='historic',
        bins=int(180/5), color = 'darkblue', 
        kde_kws={'linewidth': 2.5,'shade': True}) #'shade': True,)
    
    ax2 = sns.distplot(fut_flow, hist=False, kde=True, label='future',
        bins=int(180/5), color = 'darkred', 
        kde_kws={'linewidth': 2.5,'shade': True})

    # #extract kernel density function values
    # xhist, yhist = ax2.get_lines()[0].get_data()
    # xfut, yfut = ax2.get_lines()[1].get_data()
    # #Find the closest point on the curve
    # idx_hist = (np.abs(xhist-value)).argmin()
    # idx_fut = (np.abs(xfut-value)).argmin()
    # #Interpolate to get a better estimate
    # p_hist = np.interp(value,xhist[idx_hist:idx_hist+2],yhist[idx_hist:idx_hist+2])
    # p_fut = np.interp(value,xfut[idx_fut:idx_fut+2],yfut[idx_fut:idx_fut+2])
    # # generate cumulate distribution functions for historic and future pdfs
    # cdf_hist = scipy.integrate.cumtrapz(yhist, xhist)
    # cdf_fut = scipy.integrate.cumtrapz(yfut, xfut)
    # # calc probability of exceedance of historical 75th p flow
    # import pdb; pdb.set_trace()
    # pr_hist = cdf_hist[value]
    # pr_fut = cdf_fut[value]

    '''
    Exceedance probability calculation
    '''
    ex_prob_hist = []
    ex_value = .25 # chosen probability exceedance
    sorted_hist_flow = np.sort(hist_flow)
    n = len(sorted_hist_flow)
    for index, value in enumerate(sorted_hist_flow):
        ex_prob_hist.append((n-index+1)/float(n+1))
    idx_hist, val = min(enumerate(ex_prob_hist), key=lambda x: abs(x[1]-.25)) # need to hardcode exceedance value?
    exceedance_flow = sorted_hist_flow[idx_hist]

    ex_prob_fut = []
    n = len(fut_flow)
    sorted_fut_flow = np.sort(fut_flow)
    for index, value in enumerate(np.sort(fut_flow)):
        ex_prob_fut.append((n-index+1)/float(n+1))
    idx_fut = (np.abs(sorted_fut_flow-exceedance_flow)).argmin() # get index of exceedance flow from future data
    future_exceedance_prob = ex_prob_fut[idx_fut]

    # ax2.set_xscale('log')
    ymin, ymax = ax2.get_ylim()
    ax2.vlines(exceedance_flow,ymin=0,ymax=ymax,color='red')
    plt.ylabel('Probability density')
    plt.xlabel('Flow (m$^3$/sec)')
    ex_change = 100*(ex_value - future_exceedance_prob)
    ax2.text(.5, .5, 'Historic 75th percentile exceedance flow is {}% more likely in future conditions'.format('%.2f' % ex_change),
        horizontalalignment='center',
        verticalalignment='center',
        fontsize=11,
        transform=ax2.transAxes)
    L=plt.legend()
    fig2.savefig('data/pdfs/{}_pdf.png'.format(name))
    plt.close()
    return hist_flow, fut_flow
    