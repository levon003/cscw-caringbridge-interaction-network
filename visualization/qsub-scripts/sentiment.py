from pathlib import Path
import os
import subprocess

import pandas as pd
import numpy as np

from collections import Counter
from tqdm import tqdm

import matplotlib.pyplot as mpl
import matplotlib.dates as md
import matplotlib
import pylab as pl
from IPython.core.display import display, HTML

pwd = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/csv_data/"

def main():
    # Retrieve the empath database
    with open(os.path.join(pwd, "empath_score.csv"), 'r', encoding='utf-8') as infile:
        empaths = pd.read_csv(infile,  header=0, index_col = 0, usecols=[0,1,2,3,4,5,6])

    # Retrieve the clean author list, narrow down our empath database to journals with length > 50 who also show up in the clean list
    with open(os.path.join(pwd, "cleaned_auths.csv"), 'r', encoding='utf-8') as infile:
        authors = pd.read_csv(infile, header=0, usecols=[0,1,2,3])
        clean_emp = empaths[empaths.user_id.isin(authors.userId.values)]
        clean_emp = clean_emp[clean_emp.journal_length > 50.0]

    # Merge in timestamps to the clean empath list
    meta = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/author_type/vw/journal_author_metadata.csv"
    with open(meta, 'r', encoding='utf-8') as infile:
        timed_df = pd.read_csv(infile,  index_col=0, header=0, usecols=[0, 2, 5, 6])
        # for right now I'm keeping the how at outer since I trim this later, but could be left? 
        clean_emp = pd.merge(clean_emp, timed_df, on="journal_oid", how="outer")
        clean_emp = clean_emp.fillna(0) # catching nan predictions

    # Retrieve inflection points for each user
    with open(os.path.join(pwd, "inflections.csv"), 'r', encoding='utf-8') as infile:
        inflections = pd.read_csv(infile,  header=0)

    # Calculate score differences for FROM
    differences_df = []
    for i, user in inflections.iterrows():
        uid = user["uid"]
        if (user["from_time"] != -1):
            pt = user["from_time"]
        else:
            continue
        before_count = 0; after_count = 0;
        pre_pos_emote = 0; pos_pos_emote = 0;
        pre_neg_emote = 0; pos_neg_emote = 0;
        pre_pa_count = 0; pos_pa_count = 0;
        for j, row in clean_emp[clean_emp.user_id == uid].iterrows():
            if row["created_at"] <= pt:
                before_count += 1
                pre_pos_emote += row["positive_emotion_score"]
                pre_neg_emote += row["negative_emotion_score"]
                pre_pa_count += int(row["is_predicted_patient"])
            else:
                after_count += 1
                pos_pos_emote += row["positive_emotion_score"]
                pos_neg_emote += row["negative_emotion_score"]
                pos_pa_count += int(row["is_predicted_patient"])
        differences_df.append((int(uid), user["from_peer"], row["created_at"], before_count, after_count,
                           np.divide(pre_pos_emote, before_count), np.divide(pos_pos_emote, after_count),
                           np.divide(pre_pos_emote, before_count) - np.divide(pos_pos_emote, after_count),
                           np.divide(pre_neg_emote, before_count), np.divide(pos_neg_emote, after_count),
                           np.divide(pre_neg_emote, before_count) - np.divide(pos_neg_emote, after_count), 
                           pre_pa_count, pos_pa_count, 1))
    this_df = pd.DataFrame(differences_df, columns = ["user_id", "peer_id", "created_at", "pre_count", "post_count", 
                                                        "pre_pos", "post_pos","diff_pos", "pre_neg", "post_neg", "diff_neg",
                                                        "pre_pa_count", "post_pa_count", "is_init"])
    this_df = this_df.fillna(0)
    
    with open(os.path.join(pwd, "from_inflection.csv"), 'w', encoding='utf-8') as outfile:
        this_df.to_csv(outfile, header=True, index=False)

    # Calculate score differences for TO
    differences_df = []
    for i, user in inflections.iterrows():
        uid = user["uid"]
        if (user["to_time"] != -1):
            pt = user["to_time"]
        else:
            continue
        before_count = 0; after_count = 0;
        pre_pos_emote = 0; pos_pos_emote = 0;
        pre_neg_emote = 0; pos_neg_emote = 0;
        pre_pa_count = 0; pos_pa_count = 0;
        for j, row in clean_emp[clean_emp.user_id == uid].iterrows():
            if row["created_at"] <= pt:
                before_count += 1
                pre_pos_emote += row["positive_emotion_score"]
                pre_neg_emote += row["negative_emotion_score"]
                pre_pa_count += int(row["is_predicted_patient"])
            else:
                after_count += 1
                pos_pos_emote += row["positive_emotion_score"]
                pos_neg_emote += row["negative_emotion_score"]
                pos_pa_count += int(row["is_predicted_patient"])
        differences_df.append((int(uid), user["to_peer"], row["created_at"], before_count, after_count,
                           np.divide(pre_pos_emote, before_count), np.divide(pos_pos_emote, after_count),
                           np.divide(pre_pos_emote, before_count) - np.divide(pos_pos_emote, after_count),
                           np.divide(pre_neg_emote, before_count), np.divide(pos_neg_emote, after_count),
                           np.divide(pre_neg_emote, before_count) - np.divide(pos_neg_emote, after_count),
                           pre_pa_count, pos_pa_count, 0))
    this_df = pd.DataFrame(differences_df, columns = ["user_id", "peer_id", "created_at", "pre_count", "post_count", 
                                                        "pre_pos", "post_pos","diff_pos", "pre_neg", "post_neg", "diff_neg",
                                                        "pre_pa_count", "post_pa_count", "is_init"])
    this_df = this_df.fillna(0)
    
    with open(os.path.join(pwd, "to_inflection.csv"), 'w', encoding='utf-8') as outfile:
        this_df.to_csv(outfile, header=True, index=False)

    # Calculate score differences for OVERALL
    differences_df = []
    for i, user in inflections.iterrows():
        uid = user["uid"]
        if (user["overall_time"] != -1):
            pt = user["overall_time"]
        else:
            continue
        before_count = 0; after_count = 0;
        pre_pos_emote = 0; pos_pos_emote = 0;
        pre_neg_emote = 0; pos_neg_emote = 0;
        pre_pa_count = 0; pos_pa_count = 0;
        for j, row in clean_emp[clean_emp.user_id == uid].iterrows():
            if row["created_at"] <= pt:
                before_count += 1
                pre_pos_emote += row["positive_emotion_score"]
                pre_neg_emote += row["negative_emotion_score"]
                pre_pa_count += int(row["is_predicted_patient"])
            else:
                after_count += 1
                pos_pos_emote += row["positive_emotion_score"]
                pos_neg_emote += row["negative_emotion_score"]
                pos_pa_count += int(row["is_predicted_patient"])
        differences_df.append((int(uid), user["overall_peer"], row["created_at"], before_count, after_count,
                           np.divide(pre_pos_emote, before_count), np.divide(pos_pos_emote, after_count),
                           np.divide(pre_pos_emote, before_count) - np.divide(pos_pos_emote, after_count),
                           np.divide(pre_neg_emote, before_count), np.divide(pos_neg_emote, after_count),
                           np.divide(pre_neg_emote, before_count) - np.divide(pos_neg_emote, after_count),
                           pre_pa_count, pos_pa_count, int(user["overall_time"] == user["from_time"])))
    this_df = pd.DataFrame(differences_df, columns = ["user_id", "peer_id", "created_at", "pre_count", "post_count", 
                                                        "pre_pos", "post_pos","diff_pos", "pre_neg", "post_neg", "diff_neg",
                                                        "pre_pa_count", "post_pa_count", "is_init"])
    this_df = this_df.fillna(0)
    
    with open(os.path.join(pwd, "overall_inflection.csv"), 'w', encoding='utf-8') as outfile:
        this_df.to_csv(outfile, header=True, index=False)

if __name__ == "__main__":
    main()
