import os, sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
sys.path.insert(0, abspath(join(dirname(__file__), '..')) + '\\extract_func')
from extract_tweets import extract_tweets
from dateutil import parser
from datetime import timedelta
from Keyword_generation.gen_queries import gen_queries
import pandas as pd

df = pd.read_excel('output/HA_articles_parsed_manual_v2.xlsx')
df = df.rename({'Unnamed: 0':'id'}, axis=1)
df['Title_alt'] = df['Title'] + ' (OR Health Affairs OR healthaffairs OR health_affairs)'
# generate articles dataframe
article_df = pd.DataFrame()
article_df['Title'] = df['Title']
article_df['Keywords'] = gen_queries(df,nwords=3,stanford=True)
article_df['Start_Date'] = None
# make sure publication date is right
if df['Publication Date'].dtype == 'object':
    try:
        df['Publication Date'] = df['Publication Date'].apply(parser.parse)
    except:
        pass
article_df['End_Date'] = (df['Publication Date']).astype(str).str[0:10]
count_df = pd.DataFrame(columns=['Title','Tweet Counts'])
import pdb; pdb.set_trace()
for i in article_df[0:10].iterrows():
    print('scraping article #' + str(i[0]))
    tweet_df = extract_tweets(i[1]['Title'],i[1]['Keywords'],i[1]['Start_Date'],i[1]['End_Date'], get_replies = False, get_retweets = True)
    count_df = count_df.append(pd.Series([i[1]['Title'],len(tweet_df.index)
        + tweet_df.retweet_count.sum()],index = ['Title','Tweet Counts']),
        ignore_index = True, sort = False)
    if len(tweet_df.index) !=0 :
        tweet_df.sort_values('created_at',ascending=False).to_csv('output/retrospect/'+
            str(i[0]) + '_tweet_data.csv', index = False, encoding='utf-8')
