from newsapi import NewsApiClient
import spacy
import time
import json
import tweepy
from bs4 import BeautifulSoup
import requests as req
from textblob import TextBlob
from difflib import SequenceMatcher
from datetime import date, timedelta

class NewsSentimentAnalysis():
    
    def __init__(self, conf_file):
        self.load_configuration(conf_file)
    
    def load_configuration(self, conf_file):
        try:
            conf = open(conf_file).read()
            conf = json.loads(conf)
            if None in list(conf.values()):
                print("Please mention all the field values in the configuration")
            else:
                self.back_list_characters = conf['back_list_characters']
                self.nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
                self.newsApi = NewsApiClient(api_key=conf['news-api-key'])
                self.tweepyApi = self.getTweepyApi(conf)
                print("Configuration file loaded successfully!")
        except:
            print("Error while loading configuration file")
    
    def getTweepyApi(self, conf):
        auth = tweepy.OAuthHandler(conf['consumer-api-key'], conf['consumer-api-secret-key'])
        auth.set_access_token(conf['twitter-access-key'], conf['twitter-access-secret-key'])
        api = tweepy.API(auth)
        return api

    def getTwiterQuery(self, query):
        blob = TextBlob(query)
        return ' AND '.join(blob.noun_phrases)

    def getTweets(self, query):
        results = self.tweepyApi.search(lang="en", q=query, count=50, result_type="mixed")
        return results

    def removePunctuation(self, query):
        query = str(query.encode('utf-8', 'ignore')).replace("b'", "").replace("'", "")
        query = query.translate(str.maketrans('', '', "".join(self.back_list_characters)))
        return query

    def getTokens(self, text):
        doc = self.nlp(text)
        token_list = []
        for token in doc:
            word = token.lemma_
            if word != '-PRON-':
                token_list.append(word)
        return token_list

    def removeStopWords(self, token_list):
        passed_words =[] 
        for word in token_list:
            lexeme = self.nlp.vocab[word]
            if lexeme.is_stop == False and word != " ":
                passed_words.append(word)
        
        return passed_words

    def getTopHeadlines(self, query):
        if query and query != "":
            query = query.lower()
            top_headlines = self.newsApi.get_top_headlines(q=query, language='en')
            if len(top_headlines) < 5:
                top_headlines = self.newsApi.get_everything(q=query, language='en', from_param=(date.today()- timedelta(days=7)), to=date.today(), sort_by='relevancy')
            return top_headlines
        return None
    
    def scrapeWebPage(self, url):
        try:
            resp = req.get(url, headers = {'user-agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(str(resp.text).encode("utf-8"), "html5lib")
            temp = ''.join([ p.getText() for p in soup.find_all('p')])
            return temp
        except:
            return None

    def processUserQuery(self, query):
        clean_data = self.removePunctuation(query)
        token_list = self.getTokens(clean_data)

        clean_query = ""
        for word in self.removeStopWords(token_list):
            clean_query += word + " "

        return clean_query

    def pipeline(self, query):
        clean_query = self.processUserQuery(query)
        top_headlines = self.getTopHeadlines(clean_query)
        data = []
        for headline in top_headlines['articles'][:10]:
            data_h = self.parseHeadline(headline)
            clean_title = self.getTwiterQuery(data_h['title'])
            data_h['tweets'] = []
            for tweet in self.getTweets(clean_title):
                tweet_p = self.parseTweet(tweet)
                data_h['tweets'].append(tweet_p)
            data.append(data_h)
        return data

    def parseTweet(self, tweet):
        data = {}
        data['text'] = tweet.text
        data['location'] = tweet.user.location
        data['friends_count'] = tweet.user.friends_count
        data['favourites_count'] = tweet.user.favourites_count
        data['urls'] = [ item['expanded_url'] for item in tweet.entities['urls'] ]
        return data

    def parseHeadline(self, headline):
        if not (set({'title', 'content'}) - set(headline.keys())):
            content = headline['content']
            url = headline['url']
            temp = self.scrapeWebPage(url)
            if content and temp:
                if str(content).endswith("chars]"):
                    match = SequenceMatcher(None, content, temp).find_longest_match(0, len(content), 0, len(temp))
                    start_char = match[1]
                    end_char = int(headline['content'][263:-7]) + 260
                    news = temp[start_char:end_char]
                else:
                    news = headline['content']
            else:
                news = headline['title']
            data= {}
            data['title'] = headline['title']
            data['news_data'] = news
            data['url'] = headline['url']
            return data

    