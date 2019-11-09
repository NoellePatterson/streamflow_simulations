import glob
import os
import pandas as pd
import numpy as np
import csv
from scipy.stats import ranksums
import matplotlib.pyplot as plt
import seaborn as sns
from reference import matched_gages

def calc_metric_map(name, lat, lon, summary_dict):
    import pdb; pdb.set_trace()