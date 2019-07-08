# analyze the FDA safety announcements
# but dropping the low tweet count announcements
import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))

from analysis_func.build_msg_net import build_msg_net
import pandas as pd
import numpy as np
import networkx as nx
from networkx.algorithms.community.label_propagation import asyn_lpa_communities
from networkx.algorithms.community.modularity_max import greedy_modularity_communities
from itertools import chain
import matplotlib.pyplot as plt
# build networks for each of the safety announcements
count_df = pd.read_csv("output/tweet_counts.csv")
count_df = count_df.loc[count_df['Tweet Counts']>10]
count_df = count_df.reset_index(drop=True)
count_df.to_csv("output/FDA_safety_tweets.csv")

net_dict = {}
nodes_dict = {}
df_dict = {}
for i,file in enumerate(os.listdir('output')):
    if file[0].isnumeric():
        if i in count_df.index:
            df_dict[i] = pd.read_csv('output/'+file)
            net_dict[i] = build_msg_net(df_dict[i])
            # store list of nodes in each network
            nodes_dict[i] = [j for j,k in net_dict[i].nodes.items()]

# do a comparison of overlapping users between networks
compar_df = pd.DataFrame(index=nodes_dict.keys(),columns=nodes_dict.keys())
compar_df_alt = pd.DataFrame(index=nodes_dict.keys(),columns=nodes_dict.keys())
# define user overlap between two networks as:
# size of the overlapping set of users/# of users in the smallest network
def user_overlap(lst1, lst2,follow=False,net_key1=None,net_key2=None):
    set1 = set(lst1)
    set2 = set(lst2)
    if follow == False:
        n_overlap = len(list(set1 & set2))
        n_small_size = min(len(lst1),len(lst2))
    # option to look at overlap proportional to followers
    else:
        n_overlap = np.nansum([nx.get_node_attributes(net_dict[net_key1],
            'follower_count')[i] for i in list(set1 & set2)])
        nfol1 = np.nansum([nx.get_node_attributes(net_dict[net_key1],
            'follower_count')[i] for i in list(set1)])
        nfol2 = np.nansum([nx.get_node_attributes(net_dict[net_key2],
            'follower_count')[i] for i in list(set2)])
        n_small_size = nfol1 + nfol2 - n_overlap
    return(n_overlap/n_small_size)
for i in nodes_dict.keys():
    for j in nodes_dict.keys():
        if i != j:
            compar_df.loc[i,j] = user_overlap(nodes_dict[i],nodes_dict[j])
            compar_df_alt.loc[i,j] = user_overlap(nodes_dict[i],nodes_dict[j],True,i,j)
        else:
            compar_df.loc[i,j] = np.nan
            compar_df_alt.loc[i,j] = np.nan
# look at average overlap
#print(compar_df.mean().mean())
#print(compar_df_alt.mean().mean())

compar_df.to_csv('output/clustering/overlap_matrix_drop.csv')
compar_df_alt.to_csv('output/clustering/overlap_matrix_drop_alt.csv')

# look at clustering amongst overlaps with community detection
compar_df = compar_df.fillna(0).astype('float')
compar_df_alt = compar_df_alt.fillna(0).astype('float')
for n, c_df in enumerate([compar_df, compar_df_alt]):
    cutoff = np.quantile(list(chain(*c_df.values.tolist())),.95)
    result_df = c_df.applymap(lambda x: 1 if x>=cutoff else 0)
    compar_G = nx.from_numpy_matrix(result_df.values)
    # asyn_lpa doesn't produce much
    # compar_commun = asyn_lpa_communities(compar_G, weight='weight')
    compar_commun = greedy_modularity_communities(compar_G)

    # GMC produces a segment of 5 communities this way. let's look at the intra-
    # community clustering of these communities
    commun_subG_dict={}
    subG_means = pd.Series()
    for i,comm in enumerate(compar_commun):
        # create subgraph from community
        sub_df = result_df.loc[comm,comm]
        subG = nx.from_numpy_matrix(sub_df.values)
        commun_subG_dict[i] = subG
        subG_means.loc[i] = c_df.loc[comm,comm].mean().mean()

    # add community label to announcements
    df = pd.read_csv('output/tweet_counts.csv')
    df = df.loc[df['Tweet Counts']!=0]
    df = df.reset_index(drop=True)
    for i,comm in enumerate(compar_commun):
        df.loc[comm,'Community']=int(i)
        df.loc[comm,'Community Overlap']=subG_means.loc[i]
    if n == 0:
        df.to_csv('output/clustering/announce_communities_drop.csv')
    else:
        df.to_csv('output/clustering/announce_communities_drop_alt.csv')

# create histograms of the overlap values
c_vals = [i for j in compar_df.values for i in j]
calt_vals = [i for j in compar_df_alt.values for i in j]
plt.hist(c_vals, bins=30)
plt.title('Overlap Score Distribution')
plt.xlabel('Overlap Score')
plt.ylabel('Frequency')
plt.savefig('output/clustering/announce_drop_hist.png')
plt.clf()
plt.hist(calt_vals, bins=30)
plt.title('Weighted Overlap Score Distribution')
plt.xlabel('Overlap Score, Weighted by Followers')
plt.ylabel('Frequency')
plt.savefig('output/clustering/announce_hist_drop_alt.png')
