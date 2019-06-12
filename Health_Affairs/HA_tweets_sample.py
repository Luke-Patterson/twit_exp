import os, sys
import pandas as pd
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
sys.path.insert(0, abspath(join(dirname(__file__), '..')) + '\\extract_func')
from extract_tweets import extract_tweets

# gauge # of tweets from a bunch of different health affairs articles
articles= pd.DataFrame([
        # ['Community Paramedics, Article',[
        #     'Deploying Community Paramedics To Address Medication Complexity At Home',
        #     'healthaffairs.org/do/10.1377/hblog20190129.181994/full/'
        # ],'2019-01-30', None],
        #
        # ['Community Paramedics, Topic',[
        #     '"Community Paramedic" Medication', '"Community Paramedics" Medication',
        #     '"Community Paramedic" Medications', '"Community Paramedics" Medications',
        #     '"Community Paramedic" Medicate', '"Community Paramedics" Medicate',
        #     '"Community Paramedic" Medicates', '"Community Paramedics" Medicates',
        #     '"Community Paramedic" Drug', '"Community Paramedics" Drug',
        #     '"Community Paramedic" Drugs', '"Community Paramedics" Drugs',
        # ], None, '2019-01-29'],

        ['Meal Delivery Reduce Healthcare Costs, Article', [
            'Meal Delivery Programs Reduce The Use Of Costly Health Care In Dually Eligible Medicare And Medicaid Beneficiaries',
            'https://www.healthaffairs.org/doi/abs/10.1377/hlthaff.2017.0999'
        ], '2018-04-01', None]
    ], columns = ['Title','Keywords','Start_Date','End_Date'])

count_df = pd.DataFrame(columns=['Title','Tweet Counts'])
for i in articles.iterrows():
    tweet_df = extract_tweets(i[1]['Title'],i[1]['Keywords'],i[1]['Start_Date'],i[1]['End_Date'], get_replies = False, get_retweets = True)
    count_df = count_df.append(pd.Series([i[1]['Title'],len(tweet_df.index)
        + tweet_df.retweet_count.sum()],index = ['Title','Tweet Counts']),
        ignore_index = True, sort = False)
    tweet_df.sort_values('created_at',ascending=False).to_csv('output/'+i[1]['Title'] +'_tweet_data.csv', index = False, encoding='utf-8')
