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
df['End_Date'] = df['Start_Date'].astype('str').str[0:10]
df['Start_Date'] = None

# generate queries
df['Query'] = gen_queries(df, nwords=4)
# Add "FDA" if not already part of the query
def _chck_fda(lst):
    if 'FDA' in lst[0]:
        return(lst[0].replace('FDA',''))
    else:
        return(lst[0])
df['Query'] = df['Query'].apply(_chck_fda)
# output announcements
df.to_csv('input/FDA_announcements_keywords.csv',index=False)
# made some manual edits to the keywords
df = pd.read_csv('input/FDA_announcements_keywords_manual.csv')
# process query columns as lists
df['Query'] = df['Query'].apply(lambda x: x.split(sep=', '))
# alter dates to format needed for query
df['End_Date'] = df['End_Date'].str.replace('/','-')
# add a 0 to one digit months/dates
df['End_Date'] = df['End_Date'].apply(parser.parse)
df['End_Date'] = (df['End_Date']).astype(str).str[0:10].str.replace('/','-')
import pdb; pdb.set_trace()
count_df = pd.DataFrame(columns=['Title','Tweet Counts'])
for i in df.iterrows():
    print('scraping announcement #' + str(i[0]))
    tweet_df = extract_tweets(i[1]['Title'],i[1]['Query'],i[1]['Start_Date'],
        i[1]['End_Date'], get_replies = False, get_retweets = False, halt_count=100)
    count_df = count_df.append(pd.Series([i[1]['Title'],len(tweet_df.index)
        + tweet_df.retweet_count.sum()],index = ['Title','Tweet Counts']),
        ignore_index = True, sort = False)
    if len(tweet_df.index) !=0 :
        tweet_df.sort_values('created_at',ascending=False).to_csv('retrospect/'+
            str(i[0]) + '_' +  i[1]['Title'][0:40].replace(':','') + '_tweet_data.csv',
            index = False, encoding='utf-8')

count_df.to_csv("retrospect/tweet_counts.csv")
