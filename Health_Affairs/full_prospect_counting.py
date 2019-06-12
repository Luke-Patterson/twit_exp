# count number of articles for each article searched and compile all csvs into
# a single data frame
import pandas as pd
import numpy as np

article_df = pd.read_excel('output/HA_articles_parsed_manual_v2.xlsx')
article_df['Number of Tweets'] = 0
for i in article_df.iterrows():
    try:
        tweet_df = pd.read_csv('output/prospect/'+ str(i[0]) + '_' +
            i[1]['Title'][0:40] + '_tweet_data.csv')
        article_df.loc[i[0], 'Number of Tweets'] = len(tweet_df.index)
        if i[0] == 0:
            full_df = tweet_df
        else:
            full_df = full_df.append(tweet_df, ignore_index=True, sort=False)
    except FileNotFoundError:
        continue
article_df.to_csv('output/prospect/article_counts.csv')
full_df.to_csv('output/prospect/all_articles.csv')
