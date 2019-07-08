import tweepy
import pandas as pd
import numpy as np

# set up tweepy object
consumer_key='lu4NOuUBJoqddUXqQbMEwqWLR'
consumer_secret='gjydYC0PTbWnNZKrN4bscGr1hUcDS6V5NlzPU3n8n3wUciG2Z8'
access_token='1038416706450935808-ahzZtl4lrS1kNjIvgBwCnwsOxKqR1y'
access_token_secret='oy8TZTD7w7RWwFmuOo3SLPjDFyf6XOfMGXxJ7FJoz2CKo'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

search_titles = [
    # 'Duodenoscope',
    # 'Concussion',
    # 'Test Strips',
    # 'Medtronic',
    'Zoll LifeVest'
]

def dedup_list(seq):
   return list(set(seq))

result_df = pd.DataFrame(index=search_titles, columns = ['Spread'])

for i in search_titles:
    print(i)
    df = pd.read_csv('output/FDA_tweet_data_'+i+'.csv', encoding='utf-8')

    # get unique list of tagged and author accounts
    # authors - just take unique values of data frame
    authors = df.username.unique().tolist()

    # mentions - need to manipulate some because there are multiple mentions per tweet sometimes
    mentions = df['mentions'].str.split(pat = " ", expand = True)
    mentions = mentions.values.tolist()
    mentions = [i for j in mentions for i in j]
    mentions = dedup_list(mentions)
    mentions.remove(np.nan)

    # combine and dedup authors and mentions
    users = mentions + authors
    users = dedup_list(users)

    # now, query twitter to get number of followers for each user
    spread = 0
    for n,j in enumerate(users):
        if n % 10 == 0:
            print(str(n) + ' users queried')
        try:
            user = api.get_user(screen_name=j)
            spread += user.followers_count
        except:
            continue
    result_df.loc[i,'Spread'] = spread
result_df.to_csv('spread_results2.csv')
