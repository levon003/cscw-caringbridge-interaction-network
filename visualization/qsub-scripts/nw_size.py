import json
import numpy as np
import pandas as pd
from datetime import datetime
import csv as csv
import os
import subprocess
from tqdm import tqdm
import re
import multiprocessing as mp

pwd = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/csv_data/"

POISON = "POISON"           # this is the kill switch for the write process
epoch_day = 86400000        # accounting for milliseconds
rng = 5 * 365 * epoch_day   # we want five years of data, 1.1.2010-1.1.2016
srt = 1262304000000         # starting at 1.1.2010

with open(os.path.join(pwd, "dynamic_ints.csv"), 'r', encoding="utf-8") as ints:
    with open (os.path.join(pwd, "dynamic_auth.csv"), 'r', encoding="utf-8") as auths:
        a = pd.read_csv(auths, index_col = 0, header=None, names=("total", "first", "last"))
        i = pd.read_csv(ints, index_col = 0, header=None, names=("total", "first", "last"))

with open(os.path.join(pwd, "nw_size.csv"), 'w', encoding="utf-8") as w:
    csv_w = csv.writer(w);
    for d in tqdm(range(srt, srt + rng, epoch_day)):               
        a_slice = a.loc[(a["first"] <= d)  & (a["last"] >= d)]
        i_slice = i.loc[(i["first"] <= d) & (i["last"] >= d)]
        l_slice = pd.concat([a_slice, i_slice], axis = 1)
        auth_life = len(a_slice); int_life = len(i_slice); life = len(l_slice)
        csv_w.writerow((d, auth_life, int_life, life))
    print("Done!")
