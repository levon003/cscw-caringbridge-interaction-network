import json
import statistics as stat
import numpy as np
import pandas as pd
import csv as csv
import matplotlib.pyplot as mpl
import os
from tqdm import tqdm
import networkx as nx
from collections import defaultdict, Counter
import pickle

pwd = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/csv_data/"
dyad_dir = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/dyad_growth/"
metadata_dir = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/user_metadata"

epoch_day = 86400000             # accounting for milliseconds
epoch_yr = epoch_day * 365
srt = 1104537600000              # jan 1, 2005
rng = 12 * epoch_yr              # until jan 1, 2017 (cant multiply by floats)
month = 7 * 4 * epoch_day        # 4 weeks in one 'month'
six_months = 6 * month 

def main():
    ints = pd.read_hdf(os.path.join(dyad_dir, "h5/revised_u2u.h5"))
    author_to_site = os.path.join(metadata_dir, "interaction_metadata.h5")
    df = pd.read_hdf(author_to_site)
    sorted_df = df.sort_values(by=["user_id", "site_id", "created_at"])
    journals = sorted_df[sorted_df.int_type == "journal"]
    firsts = journals.drop_duplicates(subset=["user_id", "site_id"], keep="first")
    lasts = journals.drop_duplicates(subset=["user_id", "site_id"], keep="last")
    
    first_time = {a : b for a,b in zip(firsts.user_id, firsts.created_at)}
    last_time = {a : b for a,b in zip(lasts.user_id, lasts.created_at)}
    author_ind = {a : b for a,b in zip(firsts.index, firsts.user_id)}

    created_at_ind = {a : b for a,b in zip(ints.index, ints.created_at)}
    from_user_id_ind = {a : b for a,b in zip(ints.index, ints.from_user_id)}
    to_user_id_ind = {a : b for a,b in zip(ints.index, ints.to_user_id)}

    active_users = defaultdict(list)
    for d in tqdm(range(srt, srt + rng, month), position=0, leave=False):
        for ind in firsts.index:
            user_id = author_ind[ind]
            f = first_time[user_id]
            l = last_time[user_id]
            if f < d and l + six_months > d:
                active_users[d].append(ind)
                
    active_dyads = defaultdict(list)
    percentage_missed = defaultdict(float)
    for d in tqdm(range(srt, srt + rng, month), position=0, leave=False):
        sufficient = 0
        missed = 0
        user_list = active_users[d]
        for ind in ints.index:
            from_user_id = from_user_id_ind[ind]
            to_user_id = to_user_id_ind[ind]
            t = created_at_ind[ind]
            if t < d:
                sufficient += 1
                if from_user_id in user_list and to_user_id in user_list:
                    active_dyads[d].append((from_user_id, to_user_id))
                else:
                    missed += 1
        percentage_missed[d] = missed/sufficient
    
    should_save = True
    if should_save:
        with open(os.path.join(dyad_dir, "active_dyads.pickle"), 'wb') as f: 
            dct = dict(active_dyads)
            pickle.dump(dct, f)
        with open(os.path.join(dyad_dir, "active_users.pickle"), 'wb') as f: 
            dct = dict(active_users)
            pickle.dump(dct, f)
        with open(os.path.join(dyad_dir, "percentages.pickle"), 'wb') as f:
            dct = dict(percentage_missed)
            pickle.dump(dct, f)
    print("Finished.")
            
if __name__ == "__main__":
    main()
