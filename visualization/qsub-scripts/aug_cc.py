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
rng = 21 * 365 * epoch_day
srt = 852076800000          # starting in '97
offset = epoch_day * 7 * 4  # for decay exploration

def main():
    with open(os.path.join(pwd, "dynamic_ints.csv"), 'r', encoding="utf-8") as ints:
        with open (os.path.join(pwd, "cleaned_auths.csv"), 'r', encoding="utf-8") as auths:
            with open(os.path.join(pwd, "dynamic_pairs.csv"), 'r', encoding="utf-8") as pairs:
                a = pd.read_csv(auths, index_col = 0, header=0)
                i = pd.read_csv(ints, index_col = 0, header=None, names=("total", "first", "last"))
                p = pd.read_csv(pairs, header=None, names = ("from", "to", "first", "last", "gb", "amps", "jr"))
                a = a.astype('int64', errors='ignore')

    with open(os.path.join(pwd, "cleaned_scc.csv"), 'w', encoding="utf-8") as strong, \
    open(os.path.join(pwd, "cleaned_wcc.csv"), 'w', encoding="utf=8") as weak:
        strong_w = csv.writer(strong); weak_w = csv.writer(weak);
        for d in tqdm(range(srt, srt + rng, offset)):

            a_slice = a.loc[(a["first_update"] <= d) & (a["last_update"] + offset >= d)]
            i_slice = i.loc[(i["first"] <= d) & (i["last"] + offset >= d)]
            p_slice = p.loc[(p["first"] <= d) & (p["last"] + offset >= d)]
            l_slice = pd.concat([a_slice, i_slice], axis = 1)

            G = nx.DiGraph()
            nodes = list(set(l_slice.index))
            edges = [tuple(row) for row in p_slice[["from", "to"]].values]
            G.add_nodes_from(nodes)
            G.add_edges_from(edges)

            scc_sizes = []; wcc_sizes = [];
            for i_, connected_nodes in enumerate(sorted(nx.strongly_connected_components(G), reverse=True, key=len)):
                scc_size = len(connected_nodes)
                scc_sizes.append(scc_size)
                if i_ == 1:
                    di_s = nx.diameter(nx.DiGraph(nx.path_graph(connected_nodes)))
                    ec = nx.eccentricity(nx.DiGraph(nx.path_graph(connected_nodes)))
                    ec_s = stat.mean([ec[keys] for keys in ec]) 
            for i_, connected_nodes in enumerate(sorted(nx.weakly_connected_components(G),reverse=True, key=len)):
                wcc_size = len(connected_nodes)
                wcc_sizes.append(wcc_size)
                if i_ == 1:
                    di_w = nx.diameter(nx.DiGraph(nx.path_graph(connected_nodes)))
                    ec = nx.eccentricity(nx.DiGraph(nx.path_graph(connected_nodes)))
                    ec_w = stat.mean([ec[keys] for keys in ec])
            sorted(scc_sizes); sorted(wcc_sizes);
            
            try: 
                strong_row = (d, scc_sizes[0], scc_sizes[1], float(stat.mean([x for x in scc_sizes if x!= 1])), di_s, ec_s, len(scc_sizes) - scc_sizes.count(1), scc_sizes.count(1))
                weak_row = (d, wcc_sizes[0], wcc_sizes[1], float(stat.mean([x for x in wcc_sizes if x!= 1])), di_w, ec_w, len(scc_sizes) - wcc_sizes.count(1), wcc_sizes.count(1))
            except:
                continue
            strong_w.writerow(strong_row); weak_w.writerow(weak_row);

if __name__ == "__main__":
    main()
