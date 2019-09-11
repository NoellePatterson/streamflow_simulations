import glob
import pandas as pd
import numpy as np
import csv

class Gage:
    '''
    Organize all info on gage metrics and subsequent analysis
    '''
    # Initializer / Instance Attributes

    def __init__(self, name, metrics_file):
        self.name = name
        self.metrics_file = metrics_file


files = glob.glob('data/ffc_metrics/*')
def define_objects(files):
    for file in files:
        metrics_file = pd.read_csv(file, sep=',')
        name = file
        import pdb; pdb.set_trace()
