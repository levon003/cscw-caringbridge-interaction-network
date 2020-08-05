#!/usr/bin/env python
# coding: utf-8

# "With whom do users initiate?" Mlogit Modeling
# ===
# 
# This version is the script version.

import os
import re
import pandas as pd
import numpy as np

from collections import Counter, defaultdict
import sqlite3
from tqdm import tqdm
import random
import pickle
from datetime import datetime
import bisect

import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib
import pylab as pl
from IPython.core.display import display, HTML

import networkx as nx

import sys

# if set to True, will generate in the test data range
# Otherwise, will generate in the train data range
# This is definited by model_start_timestamp below
should_generate_test_data = True

working_dir = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/author_initiations"
assert os.path.exists(working_dir)

start_date = datetime.fromisoformat('2005-01-01')
start_timestamp = int(start_date.timestamp() * 1000)
end_date = datetime.fromisoformat('2016-06-01')
end_timestamp = int(end_date.timestamp() * 1000)
subset_start_date = datetime.fromisoformat('2014-01-01')
subset_start_timestamp = int(subset_start_date.timestamp() * 1000)

##### Data reading

# load the list of valid users
data_selection_working_dir = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/data_selection"
valid_user_ids = set()
with open(os.path.join(data_selection_working_dir, "valid_user_ids.txt"), 'r') as infile:
    for line in infile:
        user_id = line.strip()
        if user_id == "":
            continue
        else:
            valid_user_ids.add(int(user_id))


# load the list of valid sites
data_selection_working_dir = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/data_selection"
valid_site_ids = set()
with open(os.path.join(data_selection_working_dir, "valid_site_ids.txt"), 'r') as infile:
    for line in infile:
        site_id = line.strip()
        if site_id == "":
            continue
        else:
            valid_site_ids.add(int(site_id))


# read the journal metadata with author type info added
s = datetime.now()
author_type_dir = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/author_type"
journal_metadata_filepath = os.path.join(author_type_dir, "journal_metadata_with_author_type.df")
journal_df = pd.read_feather(journal_metadata_filepath)
print("Journal metadata:", datetime.now() - s)


# as a quick fix for invalid dates in journals, when created_at is 0 we use the updated_at instead
# note that only 41 updates have this issue
invalid_created_at = journal_df.created_at <= 0
journal_df.loc[invalid_created_at, 'created_at'] = journal_df.loc[invalid_created_at, 'updated_at']


health_cond_filepath = os.path.join("/home/srivbane/shared/caringbridge/data/projects/sna-social-support/user_metadata", "assigned_health_conditions.feather")
user_health_conds_df = pd.read_feather(health_cond_filepath)


# read the user author type dataframe
author_type_dir = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/author_type"
user_patient_proportions_filepath = os.path.join(author_type_dir, 'user_patient_proportions.df')
user_df = pd.read_feather(user_patient_proportions_filepath)


# read the user->user interactions dataframe
metadata_dir = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/user_metadata"
u2u_df = pd.read_feather(os.path.join(metadata_dir,"u2u_df.feather"))


# read the site-level metadata
site_metadata_working_dir = "/home/srivbane/shared/caringbridge/data/derived/site_metadata"
site_metadata_filepath = os.path.join(site_metadata_working_dir, "site_metadata.feather")
site_metadata_df = pd.read_feather(site_metadata_filepath)

# read in the geographic user assignments
geo_user_df_filepath = "/home/srivbane/shared/caringbridge/data/projects/sna-social-support/geo_data/geo_user_df.feather"
geo_user_df = pd.read_feather(geo_user_df_filepath)
geo_user_df = geo_user_df[geo_user_df.state_assignment != 'None']
valid_user_ids = valid_user_ids & set(geo_user_df.user_id)
print(f"Valid user ids reduced to a subset of geo-tagged users: {len(valid_user_ids)}")

print("Data loaded.")

# ## Compute and merge the features

# In[15]:


user_df = user_df[user_df.user_id.isin(valid_user_ids)]
user_df['is_multisite_author'] = user_df.num_sites > 1

is_mixedsite_author_dict = {}
site_author_sets = journal_df[journal_df.user_id.isin(valid_user_ids)].groupby('site_id').agg({'user_id': lambda user_ids: set(user_ids)})
for site_id, user_ids in zip(site_author_sets.index, site_author_sets.user_id):
    if len(user_ids) > 1:
        for user_id in user_ids:
            is_mixedsite_author_dict[user_id] = True
is_mixedsite_author = [user_id in is_mixedsite_author_dict for user_id in user_df.user_id]
user_df['is_mixedsite_author'] = is_mixedsite_author


# merge in the health condition data
user_health_cond_dict = {user_id: assigned_health_cond for user_id, assigned_health_cond in zip(user_health_conds_df.user_id, user_health_conds_df.assigned_health_cond)}
health_condition = [user_health_cond_dict[user_id] for user_id in user_df.user_id]
user_df['health_condition'] = health_condition


# number of journal updates, first update, last update
user_updates_df = journal_df[journal_df.user_id.isin(valid_user_ids)].groupby('user_id').agg({
    'journal_oid': lambda group: len(group),
    'created_at': lambda created_ats: (np.min(created_ats), np.max(created_ats))
}).reset_index()  # note that columns are not renamed appropriately, but are reused immediately
user_update_count_dict = {
    user_id: count for user_id, count 
    in zip(user_updates_df.user_id, user_updates_df.journal_oid)}
user_first_update_dict = {
    user_id: created_at[0] for user_id, created_at 
    in zip(user_updates_df.user_id, user_updates_df.created_at)}
user_last_update_dict = {
    user_id: created_at[1] for user_id, created_at 
    in zip(user_updates_df.user_id, user_updates_df.created_at)}
update_count = [user_update_count_dict[user_id] for user_id in user_df.user_id]
first_update = [user_first_update_dict[user_id] for user_id in user_df.user_id]
last_update = [user_last_update_dict[user_id] for user_id in user_df.user_id]
user_df['update_count'] = update_count
user_df['first_update'] = first_update
user_df['last_update'] = last_update
user_df['author_tenure'] = user_df.last_update - user_df.first_update
assert np.all(user_df.author_tenure > 0)


# posting frequency (updates per month, across all sites)
tenure_in_months = user_df.author_tenure / (1000 * 60 * 60 * 24 * 30)
user_df['update_frequency'] = user_df.update_count / tenure_in_months


# is_interacted_with
# computed from the user->user interaction data
interacted_with_user_ids = set(u2u_df.to_user_id)
is_interacted_with = [user_id in interacted_with_user_ids for user_id in user_df.user_id]
user_df['is_interacted_with'] = is_interacted_with


# is this user an initiator at any point
initiating_user_ids = set(u2u_df.from_user_id)
is_initiator = [user_id in initiating_user_ids for user_id in user_df.user_id]
user_df['is_initiator'] = is_initiator

# #### Compute the dictionary for user->(created_at)

user_updates_dict = journal_df.sort_values(by='created_at', ascending=True).groupby('user_id').agg({
    'created_at': lambda created_at: created_at.tolist()
}).created_at.to_dict()


# #### Compute the visits of the most-visited site authored by a user

# construct user->site dictionary
# contains all sites that authors have updated at least one journal update on
user_site_dict = defaultdict(set)
for row in tqdm(journal_df.itertuples(), total=len(journal_df)):
    user_site_dict[row.user_id].add(row.site_id)
# construct site->visits dictionary
site_visits_dict = {site_id: visits for site_id, visits in zip(site_metadata_df.site_id, site_metadata_df.visits)}
# construct user->visits dictionary
# pools across multiple sites by taking the site with the maximum number of visits
user_visits_dict = {user_id: max(site_visits_dict[site_id] for site_id in user_site_dict[user_id] if site_id in site_visits_dict) 
 for user_id in user_df.user_id}


# ### Filter the u2u links

valid_u2u_df = u2u_df[(u2u_df.from_user_id.isin(valid_user_ids))&(u2u_df.to_user_id.isin(valid_user_ids))]


inits_df = valid_u2u_df.sort_values(by='created_at', ascending=True).drop_duplicates(subset=['from_user_id', 'to_user_id'], keep='first')


model_start_date = datetime.fromisoformat('2014-01-01')
model_start_timestamp = int(model_start_date.timestamp() * 1000)
model_end_date = datetime.fromisoformat('2016-01-01')
model_end_timestamp = int(model_end_date.timestamp() * 1000)
if should_generate_test_data:
    model_start_date = datetime.fromisoformat('2016-01-01')
    model_start_timestamp = int(model_start_date.timestamp() * 1000)
    model_end_date = datetime.fromisoformat('2016-06-01')
    model_end_timestamp = int(model_end_date.timestamp() * 1000)


# ### Implementation of high-level graph code

class WccGraph:
    def __init__(self, node_uids):
        self.node_uids = node_uids
        self.node_dict = {}  # maps node_uid to component_uid
        self.component_dict = {}  # maps component_uid to a set of node_uids
        for component_uid, node_uid in enumerate(self.node_uids):
            self.node_dict[node_uid] = component_uid
            self.component_dict[component_uid] = set((node_uid,))
        self.edge_count = 0
        
    def add_edge(self, from_node_uid, to_node_uid):
        self.edge_count += 1
        from_component_uid = self.node_dict[from_node_uid]
        to_component_uid = self.node_dict[to_node_uid]
        if from_component_uid == to_component_uid:
            # these nodes are already weakly connected
            is_intra_component_edge = True
            from_component_size, to_component_size = 0, 0
        else:  # two different components are being merged with this edge
            is_intra_component_edge = False
            from_component_nodes = self.component_dict[from_component_uid]
            to_component_nodes = self.component_dict[to_component_uid]
            from_component_size = len(from_component_nodes)
            to_component_size = len(to_component_nodes)
            
            if from_component_size >= to_component_size:
                # merge To component into From component, deleting the To component
                from_component_nodes.update(to_component_nodes)
                del self.component_dict[to_component_uid]
                for node_uid in to_component_nodes:
                    # update the merged in component ids
                    self.node_dict[node_uid] = from_component_uid
            else:
                # merge From component into To component, deleting the From component
                to_component_nodes.update(from_component_nodes)
                del self.component_dict[from_component_uid]
                for node_uid in from_component_nodes:
                    # update the merged in component ids
                    self.node_dict[node_uid] = to_component_uid
        return is_intra_component_edge, from_component_size, to_component_size
    
    def are_weakly_connected(self, user_id1, user_id2):
        # two nodes are weakly connected if they exist in the same WCC
        return self.node_dict[user_id1] == self.node_dict[user_id2]

def compute_is_friend_of_friend(G, user_id1, user_id2):
    if len(G[user_id1]) == 0 or len(G[user_id2]) == 0:
        # if there are zero outbound edges from one of the nodes, they can't be strongly connected
        return False
    return are_fof_connected(G, user_id1, user_id2) and are_fof_connected(G, user_id2, user_id1)


def are_fof_connected(G, source, target):
    # must be a direct connection from either source -> target, or from source -> neighbor -> target
    if target in G[source]:
        return True
    for neighbor in G[source]:
        if target in G[neighbor]:
            return True
    return False


# ### Build the initial graph subset


inits_subset = inits_df[inits_df.created_at < model_start_timestamp]

s = datetime.now()
base_graph = nx.DiGraph()
nodes = set(inits_subset.from_user_id) | set(inits_subset.to_user_id)
edges = [tuple(row) for row in inits_subset[["from_user_id", "to_user_id"]].values]
base_graph.add_nodes_from(nodes)
base_graph.add_edges_from(edges)
print(f"Base graph constructed: {datetime.now() - s}")


# In[142]:


# this second graph tracks only weakly connected component info
s = datetime.now()
user_set = set(inits_df.from_user_id) | set(inits_df.to_user_id)
wcc_graph = WccGraph(user_set)
for from_user_id, to_user_id in inits_subset[["from_user_id", "to_user_id"]].values:
    wcc_graph.add_edge(from_user_id, to_user_id)
print(f"WCC graph: {datetime.now() - s}")


G = base_graph.copy()

s = 24
# use s negative samples
# valid candidate users are ALL valid authors who have posted their first update at this time
inits_subset = inits_df[(inits_df.created_at >= model_start_timestamp)&(inits_df.created_at <= model_end_timestamp)]
inits_subset = inits_subset.sort_values(by='created_at', ascending=True)

user_df['time_to_first_update'] = user_df.first_update - model_start_timestamp
# if first update is positive, it is still in the future
# if first update is <= 0, then it should already be an eligible node
# however, it might not be in the network, since the base network only contains connected nodes
active_user_ids = user_df.loc[user_df.time_to_first_update <= 0, 'user_id']


# create data structures storing all of the edges that do not yet but will exist in the model
# these will be added incrementally as computation continues
model_subset = inits_df[(inits_df.created_at >= model_start_timestamp)&(inits_df.created_at <= model_end_timestamp)]
all_edges = [(created_at, tuple(row))
             for created_at, row 
             in zip(model_subset.created_at, model_subset[["from_user_id", "to_user_id"]].values)]
edge_df = pd.DataFrame(all_edges, columns=['created_at', 'edge'])
edge_df['time_to_existence'] = edge_df.created_at - model_start_timestamp
# if time_to_existence <= 0, it should exist in the network
assert np.all(edge_df.time_to_existence > 0)


prev_timestep = model_start_timestamp
active_user_ids = user_df.loc[user_df.time_to_first_update <= 0, 'user_id']
sampled_initiations = []
for from_user_id, to_user_id, created_at in tqdm(zip(inits_subset.from_user_id, inits_subset.to_user_id, inits_subset.created_at), total=len(inits_subset)):
    curr_timestep = created_at
    elapsed_time = curr_timestep - prev_timestep
    if elapsed_time > 0:  # When the next iteration causes time to advance
        # update the active users set
        user_df.time_to_first_update -= elapsed_time
        active_user_ids = user_df.loc[user_df.time_to_first_update <= 0, 'user_id']
        # update the graph with all initiations between previous timestep and now
        edge_df.time_to_existence -= elapsed_time
        new_edge_mask = edge_df.time_to_existence < 0  # edges that exist AT zero happen at the current timestep, including the edge from_user_id, to_user_id
        new_edges = edge_df[new_edge_mask]
        edge_df = edge_df[~new_edge_mask] # TODO Use loc for assignment?
        #assert np.all(edge_df[edge_df.time_to_existence==0].created_at == created_at)
        G.add_edges_from(new_edges.edge)
        # also add edges to the WCC graph
        for from_user_id, to_user_id in new_edges.edge:
            wcc_graph.add_edge(from_user_id, to_user_id)
    
    # candidate users are all active users...
    candidate_user_ids = set(active_user_ids)
    # ... minus the true initiation target...
    candidate_user_ids.discard(to_user_id)
    # ... minus users already initiated to by this user
    if from_user_id in G:
        candidate_user_ids -= set(G[from_user_id].keys())
    
    # we only sample s of the candidate users
    negative_sampled_users = list(random.sample(candidate_user_ids, s))
    
    # now, extract ids for the target user and all of the negative sampled users
    indegree_list = []
    outdegree_list = []
    is_reciprocal_list = []
    is_weakly_connected_list = []
    is_friend_of_friend_list = []
    for user_id in [to_user_id] + negative_sampled_users:
        is_friend_of_friend = False
        if user_id in G:
            indegree = G.in_degree(user_id)
            outdegree = G.out_degree(user_id)
            is_reciprocal = from_user_id in G[user_id]
            is_weakly_connected = wcc_graph.are_weakly_connected(from_user_id, user_id)
            if is_weakly_connected:
                is_friend_of_friend = compute_is_friend_of_friend(G, from_user_id, user_id)
        else:
            indegree = 0
            outdegree = 0
            is_reciprocal = False
            is_weakly_connected = False
        
        indegree_list.append(indegree)
        outdegree_list.append(outdegree)
        is_reciprocal_list.append(is_reciprocal)
        is_weakly_connected_list.append(is_weakly_connected)
        is_friend_of_friend_list.append(is_friend_of_friend)
    
    d = {
        'initiator_user_id': from_user_id,
        'target_user_id': to_user_id,
        'negative_user_ids': negative_sampled_users,
        'created_at': created_at,
        'indegree_list': indegree_list,
        'outdegree_list': outdegree_list,
        'is_reciprocal_list': is_reciprocal_list,
        'is_weakly_connected_list': is_weakly_connected_list,
        'is_friend_of_friend_list': is_friend_of_friend_list
    }
    sampled_initiations.append(d)
    
    prev_timestep = curr_timestep


sampled_inits_df = pd.DataFrame(sampled_initiations)

# save the sampled initiations dataframe with graph features
# so that the expensive graph feature computation can be saved
sampled_inits_df_filename = "geo_sampled_inits_train_df.pickle" if not should_generate_test_data else "geo_sampled_inits_test_df.pickle"
sampled_inits_df_filepath = os.path.join(working_dir, sampled_inits_df_filename)
sampled_inits_df.to_pickle(sampled_inits_df_filepath)
print("Saved positive inits dataframe.")

# dictionaries for computing user-level features
author_type_dict = {row.user_id: row.user_author_type for row in user_df.itertuples()}
health_condition_dict = {row.user_id: row.health_condition for row in user_df.itertuples()}
is_multisite_author_dict = {row.user_id: row.is_multisite_author for row in user_df.itertuples()}
is_mixedsite_author_dict = {row.user_id: row.is_mixedsite_author for row in user_df.itertuples()}
update_count_dict = {row.user_id: row.update_count for row in user_df.itertuples()}
update_frequency_dict = {row.user_id: row.update_frequency for row in user_df.itertuples()}
state_assignment_dict = {row.user_id: row.state_assignment for row in geo_user_df.itertuples()}

# compute days_since_most_recent_update
# given a target user_id and a created_at timestamp
def get_most_recent_update(user_id, created_at):
    update_times = user_updates_dict[user_id]
    # update_times is a sorted list of created_at times for all updates by the given user_id
    ind = bisect.bisect_right(update_times, created_at)
    most_recent_update = update_times[ind-1]
    return most_recent_update

def compute_days_since_most_recent_update(user_id, created_at):
    most_recent_update = get_most_recent_update(user_id, created_at)
    ms_since_most_recent_update = created_at - most_recent_update
    days_since_most_recent_update = ms_since_most_recent_update / (1000 * 60 * 60 * 24)
    return days_since_most_recent_update

def compute_days_since_first_update(user_id, created_at):
    update_times = user_updates_dict[user_id]
    ind = bisect.bisect_right(update_times, created_at)
    most_recent_update = update_times[ind-1]
    first_update = update_times[0]
    ms_since_first_update = most_recent_update - first_update
    days_since_first_update = ms_since_first_update / (1000 * 60 * 60 * 24)
    return days_since_first_update


sampled_initiations_filename = "geo_author_initiation_choices_train_all.csv"
if should_generate_test_data:
    sampled_initiations_filename = "geo_author_initiation_choices_test_all.csv"
sampled_initiations_filepath = os.path.join(working_dir, sampled_initiations_filename)
with open(sampled_initiations_filepath, 'w') as outfile:
    header = """
            choice_id,
            initiator_user_id,
            candidate_user_id,
            is_target,
            target_outdegree,
            target_indegree,
            target_has_indegree,
            is_reciprocal,
            is_weakly_connected,
            is_friend_of_friend,
            is_author_type_shared,
            target_author_type,
            initiator_author_type,
            target_health_condition,
            is_health_condition_shared,
            target_is_multisite_author,
            target_is_mixedsite_author,
            target_update_count,
            target_update_frequency,
            target_days_since_most_recent_update,
            target_days_since_first_update,
            target_site_visits,
            is_state_assignment_shared
    """
    header = re.sub(r'\s+', '', header).strip() + "\n"
    format_str = "iiiiiiiiiiiccciiiidddii"
    outfile.write(header)
    for i, row in tqdm(enumerate(sampled_inits_df.itertuples()), total=len(sampled_inits_df)):
        choice_id = i
        initiator_user_id = row.initiator_user_id
        initiator_author_type = author_type_dict[initiator_user_id]
        initiator_health_condition = health_condition_dict[initiator_user_id]
        initiator_state_assignment = state_assignment_dict[initiator_user_id]
        for i, user_id in enumerate([row.target_user_id] + row.negative_user_ids):
            is_target = int(i == 0)
            candidate_user_id = user_id
            target_outdegree = row.outdegree_list[i]
            target_indegree = row.indegree_list[i]
            target_has_indegree = int(target_indegree > 0)
            is_reciprocal = int(row.is_reciprocal_list[i])
            is_weakly_connected = int(row.is_weakly_connected_list[i])
            is_friend_of_friend = int(row.is_friend_of_friend_list[i])
            
            # Include the user-level features for the candidates
            target_author_type = author_type_dict[candidate_user_id]
            is_author_type_shared = int(initiator_author_type == target_author_type)
            
            target_health_condition = health_condition_dict[candidate_user_id]
            is_health_condition_shared = int(initiator_health_condition == target_health_condition)
            
            target_is_multisite_author = int(is_multisite_author_dict[candidate_user_id])
            target_is_mixedsite_author = int(is_mixedsite_author_dict[candidate_user_id])
            target_update_count = update_count_dict[candidate_user_id]
            target_update_frequency = update_frequency_dict[candidate_user_id]
            
            target_days_since_most_recent_update = compute_days_since_most_recent_update(candidate_user_id, row.created_at)
            target_days_since_first_update = compute_days_since_first_update(candidate_user_id, row.created_at)
            
            target_site_visits = user_visits_dict[candidate_user_id]
            
            target_state_assignment = state_assignment_dict[candidate_user_id]
            is_state_assignment_shared = int(target_state_assignment == initiator_state_assignment)

            line_vars = [
                choice_id,
                initiator_user_id,
                candidate_user_id,
                is_target,
                target_outdegree,
                target_indegree,
                target_has_indegree,
                is_reciprocal,
                is_weakly_connected,
                is_friend_of_friend,
                is_author_type_shared,
                target_author_type,
                initiator_author_type,
                target_health_condition,
                is_health_condition_shared,
                target_is_multisite_author,
                target_is_mixedsite_author,
                target_update_count,
                target_update_frequency,
                target_days_since_most_recent_update,
                target_days_since_first_update,
                target_site_visits,
                is_state_assignment_shared
            ]
            line = ",".join([str(v) for v in line_vars]) + "\n"
            outfile.write(line)
print(f"R column types format string: {format_str}")
print(sampled_initiations_filepath)

print("Finished.")


