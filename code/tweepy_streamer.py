#Dependencies
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#Tweepy
#!pip install tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor

import twitter_credentials

#Output File (CSV)
output_data_file = 'Twitter_Output/tweets.csv'

# # # # TWITTER AUTHENTICATOR # # # #
class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth

# # # # TWITTER CLIENT # # # #
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client
    
    #Defines a function to get tweets from a user's timeline
    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    #Defines a function to get friends list for a certain twitter user
    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    #Gets all of the timeline tweets from a user's home page
    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets
# # # # TWITTER STREAMER # # # #
class TwitterStreamer():

    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()
    #Class for streaming and processing live tweets
    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        #This handles twitter authentication and the connection to the Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename) 
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
        stream.filter(track=hash_tag_list)

# # # # TWITTER STREAM LISTENER # # # # 
class TwitterListener(StreamListener):
    #Prints received tweets to stdout
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Errory on_data: %s" % str(e))
        return True
    
    def on_error(self, status):
        if status == 420:
            #Returning False on_data method in case rate limiting is happening.
            return False
        print(status)

class TweetAnalyzer():
    # Analyzing and Categorizing content #
    #Defining a function to create a datafram out of the tweets captured
    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
        #Designate the fields to be captured and turn them into columns with pandas
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        return df
        
if __name__ == '__main__':
    
    #Authenticate using twitter_credentials.py and connect to the Twitter API
    hash_tag_list = ["nationalparks", "nature", "nationalpark", "travel", "hiking", "findyourpark", 
    "naturephotography", "photography", "nationalparkgeek", "landscape", "optoutside", "adventure", 
    "landscapephotography", "nps", "roadtrip", "nationalparkservice", "mountains", "outdoors", 
    "wanderlust", "getoutside", "wildlife", "explore", "naturelovers", "bhfyp"]
    fetched_tweets_filename = "tweets.json"

    ##Grabbing tweets by hashtag
    #twitter_streamer = TwitterStreamer()
    #twitter_streamer.stream_tweets(fetched_tweets_filename, hash_tag_list)

    ##Grabbing tweets by twitter user
    #twitter_client = TwitterClient('Gladwell')
    #print(twitter_client.get_user_timeline_tweets(1))

    twitter_client=TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()

    #Using twitter API function 'user_timeline' to specify user, how many tweets
    #Most Visited NP's for backcountry campers: Grand Canyon, Yosemite, Great Smoky Mountains, 
    # Olympic, Canyonlands, Mount Rainier, Shenandoah, Yellowstone, Voyageurs

    #Most Visited NP's for tent campers: Yosemite, Joshua Tree, Great Smoky Mountains, 
    # Grand Canyon, Acadia, Sequoia, Olympic, Zion, Glacier

    #Most Visited NP's recreationally: 
    # Great Smokey Mountains (@GreatSmokyNPS) 200-399 Welcome summer!
    # Grand Canyon (@GrandCanyonNPS) 0-199 Flasgstaff
    # Yosemite (@YosemiteNPS) 400-599
    # Rocky Mountains (@RockyNPS) 600-799
    #Yellowstone (@YellowstoneNPS) 800-999
    # Zion (@ZionNPS) 1000-1199
    # Olympic (@OlympicNP) 1200-1399
    # Grand Teton (@GrandTetonNPS) 1400-1599
    # Acadia (@AcadiaNPS) 1600-1799
    tweets = api.user_timeline(screen_name='AcadiaNPS', count=400)

    #print(dir(tweets[0]))
    #print(dir(tweets[0].id))
    #print(dir(tweets[0].retweet_count))

    #Create dataframe to store content
    df = tweet_analyzer.tweets_to_data_frame(tweets)
    df.to_csv(output_data_file, mode='a', header=False)

    print(df.head(10))
    


