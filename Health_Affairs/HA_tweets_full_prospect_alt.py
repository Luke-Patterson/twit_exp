# scrape tweets prospectively for HA articles, with the topic search terms used
# retrospectively
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
df['Title'] = df.Title.str.replace('-', ' ').str.replace('/', ' ').str.replace('\', ' ').str.replace(':', ' ')
df['Title_alt'] = df['Title'] + ' (OR Health Affairs OR healthaffairs OR health_affairs)'
if df['Publication Date'].dtype == 'object':
    try:
        df['Publication Date'] = df['Publication Date'].apply(parser.parse)
    except:
        pass
df['Start_Date'] = df['Publication Date']
# generate articles dataframe
article_df = pd.read_csv('output/HA_articles_keywords_manual.csv')
article_df = article_df.drop('Start_Date',axis=1)
article_df = article_df.merge(df[['Title','Start_Date']],how='left',on='Title')
article_df['Start_Date'] = article_df['Start_Date'].astype(str).str[0:10].str.replace('/','-')
# process query columns as lists
article_df['Keywords'] = article_df['Keywords'].apply(lambda x: x.split(sep=', '))
article_df = article_df.drop_duplicates(subset='Title')
article_df['End_Date']=None
count_df = pd.DataFrame(columns=['Title','Tweet Counts'])
for i in article_df.iterrows():
    print('scraping article #' + str(i[0]))
    tweet_df = extract_tweets(i[1]['Title'],i[1]['Keywords'],i[1]['Start_Date'],
        i[1]['End_Date'], get_replies = False, get_retweets = False, halt_count=100)
    count_df = count_df.append(pd.Series([i[1]['Title'],len(tweet_df.index)
        + tweet_df.retweet_count.sum()],index = ['Title','Tweet Counts']),
        ignore_index = True, sort = False)
    if len(tweet_df.index) !=0 :
        tweet_df.sort_values('created_at',ascending=False).to_csv('output/prospect_alt/'+
            str(i[0]) + '_' +  i[1]['Title'][0:40] '_tweet_data.csv', index = False, encoding='utf-8')

count_df.to_csv("output/prospect_alt/tweet_counts.csv")
