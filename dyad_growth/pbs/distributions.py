import os
import pandas as pd
import numpy as np

from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib
import pylab as pl

def main():
    metadata_dir = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/user_metadata"

    author_to_site = os.path.join(metadata_dir, "interaction_metadata.h5")
    df = pd.read_hdf(author_to_site)
    sorted_df = df.sort_values(by=["user_id", "site_id"])
    sorted_df.head()

    current_uid = -1
    current_sid = -1
    start_date = -1
    end_date = -1
    num_relationships = 1
    tenures = []
    for i, row in sorted_df.iterrows():
        if row["user_id"] != current_uid:
            # perform our calculations
            if current_uid != -1:
                tenures.append((current_uid, (end_date - start_date) / (1000 * 60 * 60 * 24), num_relationships))
            # start a new generation
            num_relationships = 1
            current_uid = row["user_id"]
            start_date = row["created_at"]
        else:
            if row["site_id"] != current_sid:
                num_relationships += 1
            # push out the end date
        current_sid = row["site_id"]
        end_date = row["created_at"]
        
    vis_df = pd.DataFrame(tenures, columns=["uid", "tenure (days)", "num_relationships"])
    nonzero_vis_df = vis_df[vis_df["tenure (days)"] >= 0]
    one_relationship = nonzero_vis_df[nonzero_vis_df["num_relationships"] == 1]
    mlt_relationship = nonzero_vis_df[nonzero_vis_df["num_relationships"] > 1]
    print("{}% of dyads have nonnegative length".format(100 * len(nonzero_vis_df)/len(vis_df)))
    print("{}% of dyads have one relationship; {}% of dyads have >1 relationships".format(100 * len(one_relationship) / len(vis_df), 100 * len(mlt_relationship)/len(vis_df)))
    
    fig, ax = plt.subplots(2, 1, tight_layout=True, figsize=(12, 10), dpi= 200, facecolor='w', edgecolor='k')
    hist, bins, _ = ax[0].hist(nonzero_vis_df["tenure (days)"], bins=50, color='black')
    logbins = np.logspace(np.log10(bins[1]),np.log10(bins[-1]),len(bins))
    ax[1].hist(nonzero_vis_df["tenure (days)"], bins=logbins, color='black')
    ax[0].set_ylabel("Quantity")
    ax[0].set_xlabel("Days of relationship")
    ax[0].set_title("Dyadic Distribution")
    ax[1].set_ylabel("Quantity")
    ax[1].set_xlabel("Days of relationship")
    ax[1].set_title("Logarithmic Dyadic Distribution")
    ax[1].set_xscale("log")
    fig.savefig("regular.pdf", bbox_inches='tight')
    
    fig, ax = plt.subplots(2, 2, tight_layout=True, figsize=(12, 10), dpi= 200, facecolor='w', edgecolor='k')
    hist, bins, _ = ax[0][0].hist(one_relationship["tenure (days)"], bins=25, color='red')
    logbins = np.logspace(np.log10(bins[1]),np.log10(bins[-1]),len(bins))
    ax[0][1].hist(one_relationship["tenure (days)"], bins=logbins, color='red')
    ax[0][0].set_ylabel("Quantity")
    ax[0][0].set_xlabel("Days of relationship")
    ax[0][0].set_title("Dyadic Distribution")
    ax[0][1].set_ylabel("Quantity")
    ax[0][1].set_xlabel("Days of relationship")
    ax[0][1].set_title("Logarithmic Dyadic Distribution")
    ax[0][1].set_xscale("log")

    hist, bins, _ = ax[1][0].hist(mlt_relationship["tenure (days)"], bins=25, color='blue')
    logbins = np.logspace(np.log10(bins[1]),np.log10(bins[-1]),len(bins))
    ax[1][1].hist(mlt_relationship["tenure (days)"], bins=logbins, color='blue')
    ax[1][0].set_ylabel("Quantity")
    ax[1][0].set_xlabel("Days of relationship")
    ax[1][0].set_title("Dyadic Distribution")
    ax[1][1].set_ylabel("Quantity")
    ax[1][1].set_xlabel("Days of relationship")
    ax[1][1].set_title("Logarithmic Dyadic Distribution")
    ax[1][1].set_xscale("log")
    fig.savefig("num_relationships.pdf", bbox_inches='tight')
    
if __name__ == "__main__":
    main()
