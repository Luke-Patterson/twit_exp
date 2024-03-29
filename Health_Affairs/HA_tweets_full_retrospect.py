# scrape tweets retrospectively for HA articles
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
if df['Publication Date'].dtype == 'object':
    try:
        df['Publication Date'] = df['Publication Date'].apply(parser.parse)
    except:
        pass
df['End_Date'] = df['Publication Date']
# generate articles dataframe
article_df = pd.DataFrame()
article_df['Title'] = df['Title']
article_df['Keywords'] = gen_queries(df,nwords=4,stanford=False)
article_df['Keywords'] =article_df['Keywords'].apply(lambda x: x[0])
article_df['Start_Date'] = None
# export to csv for manual analysis
article_df.to_csv('output/HA_articles_keywords.csv', index = False)
# reload manual edits
article_df = pd.read_csv('output/HA_articles_keywords_manual.csv')
# make sure publication date is right
article_df = article_df.merge(df[['Title','End_Date']],how='left',on='Title')
article_df['End_Date'] = article_df['End_Date'].astype(str).str[0:10].str.replace('/','-')
# manual end dates that can't merge due to changes in Title
article_df.loc[0,'End_Date'] = '2016-10-01'
article_df.loc[12,'End_Date'] = '2018-11-01'
article_df.loc[16,'End_Date'] = '2012-01-01'
article_df.loc[22,'End_Date'] = '2012-11-01'
article_df.loc[23,'End_Date'] = '2016-09-01'
article_df.loc[24,'End_Date'] = '2014-04-01'
article_df.loc[26,'End_Date'] = '2009-01-01'
article_df.loc[32,'End_Date'] = '2018-12-01'
# process query columns as lists
article_df['Keywords'] = article_df['Keywords'].apply(lambda x: x.split(sep=', '))
article_df = article_df.drop_duplicates(subset='Title')
article_df.to_csv('output/HA_articles_keywords_manual_final.csv')
count_df = pd.DataFrame(columns=['Title','Tweet Counts'])
for i in article_df.iterrows():
    print('scraping article #' + str(i[0]))
    tweet_df = extract_tweets(i[1]['Title'],i[1]['Keywords'],i[1]['Start_Date'],
        i[1]['End_Date'], get_replies = False, get_retweets = False, halt_count=100)
    count_df = count_df.append(pd.Series([i[1]['Title'],len(tweet_df.index)
        + tweet_df.retweet_count.sum()],index = ['Title','Tweet Counts']),
        sort = False)
    if len(tweet_df.index) !=0 :
        tweet_df.sort_values('created_at',ascending=False).to_csv('output/retrospect/'+
            str(i[0]) + '_' +  i[1]['Title'][0:40] + '_tweet_data.csv', index = False, encoding='utf-8')
count_df.to_csv("output/retrospect/tweet_counts.csv")
