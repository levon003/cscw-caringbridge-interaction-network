from pathlib import Path
import os
import subprocess

import pandas as pd
import numpy as np

from collections import Counter
from tqdm import tqdm
import csv as csv
import pickle

import pylab as pl
from IPython.core.display import display, HTML

pwd = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/csv_data/"

def main():
    auths = pd.read_csv(os.path.join(pwd, "jo.csv"), names=["from_userId", "site_id", "to_userId", "type", "ts"])
    df = pd.read_csv(os.path.join(pwd, "jo.csv"), names=["from_userId", "site_id", "to_userId", "type", "ts"])

    with open(os.path.join(pwd, "ints.csv"), 'r', encoding='utf-8') as ints:
       csv_r = csv.reader(ints);
       for row in csv_r:
           if row[0] in auths.from_userId:
               df.append(row)
    
    ia = {}
    with open(os.path.join(pwd, "interactivity.pickle"), 'wb') as difs:
        for key, group in tqdm(df.groupby(by='from_userId', sort=False)):
            if len(group) < 10:
                continue  # only include users who had at least 10 interactions
            timestamps = sorted(group.ts)
            interactivity_times = np.diff(timestamps)
            ia[str(key)] = interactivity_times
        pickle.dump(ia, difs, protocol = pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    main()
