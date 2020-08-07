import json
import statistics as stat
import numpy as np
import pandas as pd
import csv as csv
import os
from tqdm import tqdm
import networkx as nx

pwd = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/csv_data/"

epoch_day = 86400000        # accounting for milliseconds
epoch_fwk = 7 * 4 * epoch_day 
rng = 21 * 365 * epoch_day   # we want five years of data, 1.1.2010-1.1.2016
srt = 852076800000         # starting in '97

def main():
    with open(os.path.join(pwd, "dynamic_ints.csv"), 'r', encoding="utf-8") as ints:
        with open (os.path.join(pwd, "dynamic_auth.csv"), 'r', encoding="utf-8") as auths:
            with open(os.path.join(pwd, "dynamic_pairs.csv"), 'r', encoding="utf-8") as pairs:
                a = pd.read_csv(auths, index_col = 0, header=None, names=("total", "first", "last"))
                i = pd.read_csv(ints, index_col = 0, header=None, names=("total", "first", "last"))
                p = pd.read_csv(pairs, header=None, names = ("from", "to", "first", "last", "gb", "amps", "jr"))

        with open(os.path.join(pwd, "l_strong.csv"), 'w', encoding="utf-8") as strong, \
        open(os.path.join(pwd, "l_weak.csv"), 'w', encoding="utf=8") as weak:
            strong_w = csv.writer(strong); weak_w = csv.writer(weak);
            for d in tqdm(range(srt, srt + rng, epoch_fwk)):

                a_slice = a.loc[(a["first"] <= d) & (a["last"] >= d)]
                i_slice = i.loc[(i["first"] <= d) & (i["last"] >= d)]
                p_slice = p.loc[(p["first"] <= d) & (p["last"] >= d)]
                l_slice = pd.concat([a_slice, i_slice], axis = 1)

                G = nx.DiGraph()
                nodes = list(set(l_slice.index))
                edges = [tuple(row) for row in p_slice[["from", "to"]].values]
                G.add_nodes_from(nodes)
                G.add_edges_from(edges)

                scc_sizes = []; wcc_sizes = [];
                for i_, connected_nodes in enumerate(sorted(nx.strongly_connected_components(G), key=len, reverse=True)):
                    scc_size = len(connected_nodes)
                    scc_sizes.append(scc_size)
                for i_, connected_nodes in enumerate(sorted(nx.weakly_connected_components(G), key=len, reverse=True)):
                    wcc_size = len(connected_nodes)
                    wcc_sizes.append(wcc_size)

                sorted(scc_sizes); sorted(wcc_sizes);
                
                try:
                    strong_row = (d, scc_sizes[0], scc_sizes[1], float(stat.mean([x for x in scc_sizes if x!=1])), scc_sizes.count(1))
                    weak_row = (d, wcc_sizes[0], wcc_sizes[1], float(stat.mean([x for x in wcc_sizes if x!=1])), wcc_sizes.count(1))
                except:
                     continue
                strong_w.writerow(strong_row); weak_w.writerow(weak_row);

if __name__ == "__main__":
     main()
