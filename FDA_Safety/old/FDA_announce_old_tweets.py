import got_mod as got
import time
import datetime
import pandas as pd
start = datetime.datetime.now()
search_titles = [
    'Duodenoscope',
    'Concussion',
    'Test Strips',
    'Medtronic',
    'Zoll LifeVest'
]
search_keywords=[
    ['fda%20Duodenoscope%20OR%20Reprocessing','fda%20Duodenoscopes%20OR%20Reprocessing'],
    ['fda%20concussion','fda%20"head%20injury"'],
    ['fda%20"test%20strip"','fda%20"test%20strips"'],
    ['fda%20cybersecurity%20OR%20medtronic','fda%20"implantable%20cardiac"'],
    ['fda%20lifevest%20OR%20cardioverter%20OR%20defibrillator']
]
search_start_dates= [
    "2019-04-12",
    "2019-04-10",
    "2019-04-08",
    "2019-03-21",
    "2019-03-06"
]

for s,kwords,date in zip(search_titles,search_keywords,search_start_dates):
    count = 0
    for g in kwords:
        tweetCriteria = got.manager.TweetCriteria().setQuerySearch(g).setSince(date)
        tweets = got.manager.TweetManager.getTweets(tweetCriteria)
        def printTweet(descr, t):
            print(descr)
            print("Username: %s" % t.username)
            print("Retweets: %d" % t.retweets)
            print("Text: %s" % t.text)
            print("Mentions: %s" % t.mentions)
            print("Hashtags: %s\n" % t.hashtags)
        # for i,j in enumerate(tweets):
        #     printTweet("Tweet # "+str(i), j)

        print(datetime.datetime.now() - start)

        if count == 0:
            # extract tweets into data frame
            tweet_props = ['id', 'permalink', 'username', 'text', 'date', 'retweets',
                'favorites', 'hashtags', 'mentions', 'geo']
            tweet_df = pd.DataFrame(columns = tweet_props.append('keyword'), index=range(len(tweets)))
            for i,t in enumerate(tweets):
                tweet_df.loc[i, 'id'] = t.id
                tweet_df.loc[i, 'permalink'] = t.permalink
                tweet_df.loc[i, 'username'] = t.username
                tweet_df.loc[i, 'text'] = t.text
                tweet_df.loc[i, 'date'] = t.date
                tweet_df.loc[i, 'retweets'] = t.retweets
                tweet_df.loc[i, 'favorites'] = t.favorites
                tweet_df.loc[i, 'hashtags'] = t.hashtags
                tweet_df.loc[i, 'mentions'] = t.mentions
                tweet_df.loc[i, 'geo'] = t.geo
                tweet_df.loc[i, 'keyword'] = g
            mark = len(tweet_df.index)
        else:
            print(mark)
            for i,t in enumerate(tweets):
                tweet_df.loc[i + mark, 'id'] = t.id
                tweet_df.loc[i + mark, 'permalink'] = t.permalink
                tweet_df.loc[i + mark, 'username'] = t.username
                tweet_df.loc[i + mark, 'text'] = t.text
                tweet_df.loc[i + mark, 'date'] = t.date
                tweet_df.loc[i + mark, 'retweets'] = t.retweets
                tweet_df.loc[i + mark, 'favorites'] = t.favorites
                tweet_df.loc[i + mark, 'hashtags'] = t.hashtags
                tweet_df.loc[i + mark, 'mentions'] = t.mentions
                tweet_df.loc[i + mark, 'geo'] = t.geo
                tweet_df.loc[i + mark, 'keyword'] = g
            mark = len(tweet_df.index)
        count +=1
    tweet_df = tweet_df.drop_duplicates('id')
    import pdb; pdb.set_trace()
    tweet_df.to_csv('output/FDA_tweet_data_'+s+'.csv', encoding='utf-8')
