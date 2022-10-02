import re
import tweepy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from configparser import ConfigParser
from better_profanity import profanity

def get_api(nameConfig='config', nameSection='blog_r_'):
    
    config = ConfigParser()
    config.read(nameConfig+'.ini')
    consumer_key = config.get(nameSection, 'key')
    consumer_secret = config.get(nameSection, 'secret')
    access_token = config.get(nameSection, 'access_token')
    access_secret = config.get(nameSection, 'access_secret')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
    
    return api


def get_tweets(api, word, numtweet, language, type_tweet='mixed'):
    
    def __get_information_tweet(tweet):
    
        '''
        This function allow us to get information about the tweet
        Parameters:
            fromAccount: This parameter just allow the value True or False.
        '''
        
        idTweet = tweet.id_str
        date_tweet_complete = tweet.created_at
        date_tweet = date_tweet_complete.strftime('%Y-%m-%d')
        hour_tweet = date_tweet_complete.strftime('%H:%M:%S')
        username = tweet.user.screen_name
        description = tweet.user.description
        location = tweet.user.location
        following = tweet.user.friends_count
        followers = tweet.user.followers_count
        totaltweets = tweet.user.statuses_count
        retweetcount = tweet.retweet_count
        favoritecount = tweet.favorite_count
        text = tweet.text if hasattr(tweet, 'text') == True else tweet.full_text
        hashtagsTweet = []
        for i in range(len(tweet.entities['hashtags'])):
            hashtagsTweet.append(tweet.entities['hashtags'][i]['text'])

        listFinal = [idTweet, date_tweet, hour_tweet, username, description, location, following, followers, totaltweets, retweetcount, favoritecount, text, hashtagsTweet]

        return listFinal
    
    db = pd.DataFrame(columns=['searched_word', 'id_tweet', 'date_tweet', 'hour_tweet', 'username', 'description', 'location', 'following', 'followers', 'totaltweets', 'retweetcount', 'favoritecount', 'text', 'hashtags'])
    noRt = ' -filter:retweets'
    tweets = tweepy.Cursor(api.search_tweets, q=word + noRt, lang=language, tweet_mode='extended', result_type=type_tweet).items(numtweet)  
    list_tweets = [tweet for tweet in tweets]

    for tweet in list_tweets:
        ith_tweet = __get_information_tweet(tweet)
        db.loc[len(db)] = [word] + ith_tweet

    return db


def clean_tweet(tweet):
    
    if type(tweet) == float:
        return ""
    
    r = tweet.lower()
    r = profanity.censor(r)
    r = re.sub("'", "", r) # This is to avoid removing contractions in english
    r = re.sub("@[A-Za-z0-9_]+","", r)
    r = re.sub("#[A-Za-z0-9_]+","", r)
    r = re.sub(r'http\S+', '', r)
    r = re.sub('[()!?]', ' ', r)
    r = re.sub('\[.*?\]',' ', r)
    r = re.sub("[^a-z0-9]"," ", r)
    r = r.split()
    stopwords = ["for", "on", "an", "a", "of", "and", "in", "the", "to", "from"]
    r = [w for w in r if not w in stopwords]
    r = " ".join(word for word in r)
    
    return r


def pie_plot(df, col, title, size=(8, 6)):
    
    fig, ax = plt.subplots(figsize=size)

    observation_values = list(df[col].value_counts().index)
    total_observation_values = list(df[col].value_counts())
    ax.pie(total_observation_values, labels= observation_values, autopct = '%1.1f%%', startangle = 110, labeldistance = 1.1)
    ax.axis("equal") # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title(title)
    plt.legend()
    plt.show()
    
    
def plot_wordCloud(df, col, size=(10, 7)):
    
    all_words = ' '.join([text for text in df[col].tolist()])
    wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(all_words)

    plt.figure(figsize=size)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis('off')
    plt.show()
