import pandas as pd

art_df = pd.read_csv('output/Community Paramedics, Article_tweet_data.csv')
topic_df = pd.read_csv('output/Community Paramedics, Topic_tweet_data.csv')

# note which ones are related to article:
topic_df['Article'] = 0
topic_df.loc[topic_df['id'] in art_df['id'], 'Article'] = 1
