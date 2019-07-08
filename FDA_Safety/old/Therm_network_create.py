# create a sample network from the sample tweet data
import pandas as pd
import networkx as nx
import numpy as np
from ast import literal_eval
import re
import matplotlib.pyplot as plt

# get raw csv of tweets
df = pd.read_csv('output/FDA_tweet_data.csv', index_col=0)
df.mentions = df.mentions.str.replace('@US_','@US_FDA')
unique_nodes = df.username.unique().tolist()

# extract users mentioned in tweets
# find the @'s
def find_at(x):
    return([m.start() for m in re.finditer('@',x)])
at_locs =  df.text.apply(find_at)
at_locs = at_locs.rename('locs')
def get_users(str, locs):
    users = []
    for i in locs:
        user = str[i+1:].split()[0]
        users.append(user)
    return(users)
text_df = pd.concat([df.text, at_locs],axis=1)
unique_df = text_df.apply(lambda x: get_users(x[0], x[1]), axis = 1)
unique_df = unique_df.apply(lambda x: [i.replace(':','') for i in x])
# add unique users to a separate data frame
def unique_list(list):
    used = set()
    unique = [x for x in list if x not in used and (used.add(x) or True)]
    return unique
unique_df = unique_df.apply(unique_list)

# split up the resulting series of lists into a separate dataframe
to_users = unique_df.apply(lambda x: ' '.join(x))
to_users = to_users.str.split(pat=" ",expand=True)

# create object of counts of mentions
to_users_count = pd.Series([j for i in to_users.values.tolist() for j in i]).value_counts()

# add unique list of all users mentioned to unique_nodes
unique_to = list(set([j for i in to_users.values.tolist() for j in i]))
unique_to.remove('')
unique_nodes.append(unique_to)
unique_nodes = list(set([j for i in unique_nodes for j in i]))

# create directed edges based on authors and mentions
# merge to and from users
edge_df = pd.concat([from_users,to_users],axis=1)
# flag retweets to reverse direction of edges
edge_df['RT_flg'] = 0
edge_df.loc[df.text.str[0:2] == 'RT','RT_flg'] = 1


# convert to tuples
edge_tuples = []
for i,j in edge_df.iterrows():
    for k in range(len(j)-1):
        if j[k] != None:
            if j['RT_flg'] == 0:
                if j[k] == '':
                    edge_tuples.append((j['user'],j['user']))
                else:
                    edge_tuples.append((j['user'],j[k]))
            if j['RT_flg'] == 1:
                if j[k] == '':
                    edge_tuples.append((j['user'],j['user']))
                else:
                    edge_tuples.append((j[k],j['user']))
# create network
G= nx.DiGraph()
G.add_nodes_from(unique_nodes)
G.add_edges_from(edge_tuples)

# some basic analysis of the network created
# most prolific tweeters
outdeg_df = pd.DataFrame([[node,val] for (node, val) in sorted(G.out_degree, key=lambda x: x[1], reverse=True)])
outdeg_df.columns = ['Account', 'Tweets sent']

# most prolific receivers of tweets
indeg_df = pd.DataFrame([[node,val] for (node, val) in sorted(G.in_degree, key=lambda x: x[1], reverse=True)])
indeg_df.columns = ['Account', 'Tweets received']
