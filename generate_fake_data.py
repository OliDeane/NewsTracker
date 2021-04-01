import configparser
from twython import Twython
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import numpy as np
from getpass import getpass

import matplotlib.pyplot as plt 
import matplotlib
from matplotlib import rcParams
import json

def get_timeline_posts(twitter):
    """ Fetches recent tweets from user's timeline """
    params = {'count':800, 'contributor_details':False, 'exclude_replies':True}
    home = twitter.get_home_timeline(**params)

    return home, params

def get_likes(params):
    # Get the posts that the user has favorited
    liked_posts = twitter.get_favorites(**params)
    liked_list_ids = [liked_posts[i]['id_str'] for i in range(len(liked_posts))]

    return liked_list_ids

def get_linked_text(url):

    # url = home[5]['entities']['urls'][0]['expanded_url']
    req = requests.get(url)
    source = req.text
    soup = BeautifulSoup(source, 'html.parser')
    body = soup.text

    # clean the body
    clean_body = ' '.join(re.sub("(</[a-zA-Z]>)|(<[a-zA-Z]>)|(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", body).split())

    return clean_body

def get_link_data(post):
    """ Extracts link and article text on link landing page """
    try:
        link = post['entities']['urls'][0]['expanded_url']
        if 'twitter.com' in link:
            link = np.NaN
        linked_text = np.NaN#get_linked_text(link)
    except:
        link = np.NaN
        linked_text = np.NaN
    
    return link, linked_text

def get_political_score(post, pol_dict):
    """ Saves politics score from the saved json file """ 

    try:
        pol_score = pol_dict[post['user']['name']]
    except:
        pol_score = np.NaN
    
    return pol_score

def check_if_liked(post, liked_list_ids):
    if post['id_str'] in liked_list_ids:
        liked = 1
    else:
        liked = 0
    
    return liked

def generate_raw_data(home, liked_list_ids, pol_dict):
    data_dict = {'date':[], 'names':[], 'locs':[], 'tweet_texts':[], 'links':[], 'linked_text':[], 'politics_score':[], 'liked':[]}

    for post in home:
        # Get the URLs
        link, linked_text = get_link_data(post)

        pol_score = get_political_score(post, pol_dict)

        liked = check_if_liked(post, liked_list_ids)



        post_dict = {'date':[post['created_at'][4:10]], 'names':[post['user']['name']], 'locs':[post['user']['location']], 'tweet_texts':[post['text']], 'links':[link], 'linked_text':[linked_text], 'politics_score':[pol_score], 'liked':[liked]}

        data_dict = {key: value + post_dict[key] for key, value in data_dict.items()}

    # Save to a pandas dataframe
    raw_data = pd.DataFrame(data = data_dict)

    return raw_data

if __name__ == '__main__':

    # Load in political dictionary
    with open('political_leanings.json', 'r') as fp:
        pol_dict = json.load(fp)

    # set up API
    APP_KEY = getpass("API_KEY: ")
    APP_SECRET = getpass("API_KEY_SECRET: ")
    OAUTH_TOKEN = getpass("ACCESS_TOKEN: ")
    OAUTH_TOKEN_SECRET = getpass("ACCESS_SECRET: ")
    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    # Fetch most recent posts
    home, params = get_timeline_posts(twitter)

    # Fetch liked posts
    liked_list_ids = get_likes(params)
    
    # Get full raw data csv
    raw_data = generate_raw_data(home, liked_list_ids, pol_dict)

    print(raw_data.head(10))

    # Save to a csv
    # raw_data.to_csv('example_raw_data')