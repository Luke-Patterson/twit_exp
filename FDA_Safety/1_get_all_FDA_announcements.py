# extract all FDA announcements
import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
sys.path.insert(0, abspath(join(dirname(__file__), '..')) + '\\extract_func')

from extract_tweets import extract_tweets
from Keyword_generation.gen_queries import gen_queries
from dateutil import parser
from datetime import timedelta
import pandas as pd

df = pd.read_excel('input/FDA_Announcements.xlsx')
df = df.rename({'Text':'Title', 'Date':'Start_Date'},axis=1)
df['Start_Date'] = df['Start_Date'].astype('str').str[0:10]
df['End_Date'] = None
# generate queries
df['Query'] = gen_queries(df, nwords=4)
# Add "FDA" if not already part of the query
def _chck_fda(lst):
    if 'FDA' in lst[0]:
        return(lst[0])
    else:
        return(lst[0]+ ' FDA')
df['Query'] = df['Query'].apply(_chck_fda)
# check for both link and Keywords
df['Keywords'] = df[['Query','Link']].apply(lambda x: [x['Query'], x['Link']], axis=1)

count_df = pd.DataFrame(columns=['Title','Tweet Counts'])
for i in df.iterrows():
    print('scraping announcement #' + str(i[0]))
    tweet_df = extract_tweets(i[1]['Title'],i[1]['Keywords'],i[1]['Start_Date'],
        i[1]['End_Date'], get_replies = False, get_retweets = True)
    count_df = count_df.append(pd.Series([i[1]['Title'],len(tweet_df.index)
        + tweet_df.retweet_count.sum()],index = ['Title','Tweet Counts']),
        ignore_index = True, sort = False)
    if len(tweet_df.index) !=0 :
        tweet_df.sort_values('created_at',ascending=False).to_csv('output/'+
            str(i[0]) + '_' +  i[1]['Title'][0:40].replace(':','') + '_tweet_data.csv',
            index = False, encoding='utf-8')

count_df.to_csv("output/tweet_counts.csv")
