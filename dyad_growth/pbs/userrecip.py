import os
import pandas as pd
import numpy as np

from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib
import pylab as pl
from tqdm import tqdm
from collections import defaultdict

def main():
    u2u_reduced = pd.read_hdf("../revised_u2u.h5")
    recips = pd.DataFrame(columns=["from_user_id", "to_user_id", "created_at", "int_type"])
    u2u_copy = u2u_reduced.copy()
    for i, row in u2u_copy.iterrows():
        match = u2u_copy[(u2u_copy["from_user_id"] == row["to_user_id"]) & (u2u_copy["to_user_id"] == row["from_user_id"])]
        if len(match) > 0:
            recips = pd.concat([recips, match], sort=True)
            u2u_copy.drop(i)
            u2u_copy.drop(match.index)
    nonrecips = u2u_reduced[~u2u_reduced.index.isin(recips.index)]
    recips.to_hdf("../revised_recips.h5", key="recips")
    nonrecips.to_df("../revised_nonrecips.h5", key="nonrecips")
    
if __name__ == "__main__":
    main()