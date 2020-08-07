from pathlib import Path
import os
import subprocess
import sys

import pandas as pd
import numpy as np

from collections import Counter
from tqdm import tqdm

import matplotlib.pyplot as mpl
import matplotlib.dates as md
import matplotlib
import pylab as pl
from IPython.core.display import display, HTML
import statistics as stat

pwd = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/csv_data/"

epoch_day = 86400000        # accounting for milliseconds

def f(row):
    if row['overall_time'] == row['from_time']:
        val = row['from_peer']
    else:
        val = row['to_peer']
    return val

def main():
    with open(os.path.join(pwd, "cleaned_auths.csv"), 'r', encoding='utf-8') as infile:
        authors = pd.read_csv(infile, header=0, usecols=[0,1,2,3])
    with open(os.path.join(pwd, "dynamic_pairs.csv"), 'r', encoding='utf-8') as ints:
        ints_df = pd.read_csv(ints, usecols = [0,1,2,3], names = ["from", "to", "first", "last"])
        ints_df = ints_df[(ints_df["from"].isin(authors.userId.values)) & (ints_df["to"].isin(authors.userId.values))]

    ints_df = ints_df.sort_values(by=["from"])
    inflection_pts = []
    which = -1; 
    my_pts = []
    for index, row in ints_df.iterrows():
        mini = sys.maxsize; rec = -1;
        if row["from"] != which:
            if which != -1:
                for tup in my_pts:
                    if tup[0] < mini:
                        mini = tup[0]
                        rec = tup[1]
                inflection_pts.append((which, mini, rec))
            which = row["from"]
            my_pts = []
        my_pts.append((row["first"], row["to"],))
    inflections_from = pd.DataFrame(inflection_pts, columns = ["uid", "from_time", "from_peer"])
    
    ints_df = ints_df.sort_values(by=["to"])
    inflection_pts = []
    which = -1; 
    my_pts = []
    for index, row in ints_df.iterrows():
        mini = sys.maxsize; rec = -1;
        if row["to"] != which:
            if which != -1:
                for tup in my_pts:
                    if tup[0] < mini:
                        mini = tup[0]
                        rec = tup[1]
                inflection_pts.append((which, mini, rec))
            which = row["to"]
            my_pts = []
        my_pts.append((row["first"], row["from"],))
    inflections_to = pd.DataFrame(inflection_pts, columns = ["uid", "to_time", "to_peer"])
    
    inflections = pd.merge(inflections_from, inflections_to, on="uid", how="outer")    
    
    inflections["overall_time"] = inflections[['from_time','to_time']].min(axis=1)
    inflections["overall_peer"] = inflections.apply(f, axis=1)
    inflections = inflections.fillna(-1)
    inflections = inflections.replace(sys.maxsize, -1)
    
    with open(os.path.join(pwd, "inflections.csv"), 'w', encoding="utf-8") as outfile:
        inflections.to_csv(outfile, header=True, index=False)

if __name__ == "__main__":
    main()