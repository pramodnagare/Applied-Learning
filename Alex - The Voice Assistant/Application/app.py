from googlesearch import search
from bs4 import BeautifulSoup
import requests as req
from newsapi import NewsApiClient
from nltk.corpus import words
import pyttsx3
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import speech_recognition as sr
import spacy
from datetime import date, timedelta, datetime
import wikipedia

class Alex:

    def __init__(self, conf):

        self.nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
        self.black_list_characters = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        self.newsapi = NewsApiClient(api_key=conf['news-api-key'])
        self.app_trigger_name = str(conf['app-trigger-name']).lower() if conf['app-trigger-name'] else "Alex"
        self.introduce()

    def analyseQuery(self, query):
        if query and "{} stop".format(self.app_trigger_name) in query.lower():
            self.speak("OK Bye!")
            exit()
        
        elif query:
            query = str(query).lower()
            if query.startswith(self.app_trigger_name):
                query = query.replace(self.app_trigger_name, "")
                if len(query) > 3:
                    self.processQuery(query)

    def speak(self, text):
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
        engine.say(text)
        engine.runAndWait()

    def introduce(self):
        hour = int(datetime.now().hour)
        if hour>=0 and hour<12:
            self.speak("Good Morning!")
        elif hour>=12 and hour<18:
            self.speak("Good Afternoon!")
        else:
            self.speak("Good Evening!")
        self.speak("I am {}. How may I help you?".format(self.app_trigger_name))

    def takeCommand(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.pause_threshold = 0.5
            audio = r.listen(source)

        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")

        except: 
            print("Say that again please...")
            return None
        return query

    def removePunctuation(self, query):
        query = str(query.encode('utf-8', 'ignore')).replace("b'", "")
        query = query.translate(str.maketrans('', '', self.black_list_characters))
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

    def getTopWords(self, total_content, query):
        
        token_list = self.getTokens(total_content)

        passed_words = self.removeStopWords(token_list)

        unique_words = set(passed_words) 
        freq_data = {}
        for words in unique_words : 
            freq_data[words] = passed_words.count(words)
        
        top_words = sorted(freq_data.items(), key = lambda kv:(kv[1], kv[0]), reverse=True,)

        return_list = []
        for item in top_words:
            if item not in query.split(" "):
                return_list.append(item)
                if len(return_list) == 3:
                    break

        return return_list

    def tryWiki(self, query):
        try:
            results = wikipedia.summary(query, sentences=10)
            results = results.replace("\n", " ").split(". ")
            self.speak("According to Wikipedia")
            self.speak(results[0:2])
            
            for item in process.extract(query, results[2:], limit=1):
                print(item)
                self.speak(item[0])
            return True

        except Exception as e:
            return False

    def tryNews(self, query):
        if query and query != "":
            top_headlines = self.newsapi.get_everything(q=query, language='en', from_param=(date.today()- timedelta(days=7)), sort_by='relevancy')

            if len(top_headlines['articles']) >= 2:
                total_content = ""
                for news in top_headlines['articles']:
                    if "content" in news.keys():
                        total_content += str(news['content']).lower()
                total_content = self.removePunctuation(total_content)
                top_words = self.getTopWords(total_content, query)

                context = ""
                for item in top_words:
                    context += item[0] +" "
                
                return context, top_headlines['articles'][0]
        
        return None, None

    def scrapWebPage(self, url):
        print("Searching for: ", url)
        resp = req.get(url, headers = {'user-agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(str(resp.text).encode("utf-8"), "html5lib")

        for script in soup(["script", "style"]):
            script.extract()

        possible_answers = [ p.getText() for p in soup.find_all('p')]

        if len(possible_answers) < 10:
            possible_answers = []
            for item in soup.find_all('div', recursive=True):
                temp_list = item.getText(strip=True, separator="**").split("**")
                for temp_item in temp_list:
                    if len(temp_item) >50:
                        possible_answers.append(temp_item)
        
        return possible_answers

    def getBestResult(self, query, possible_answers):
        status = False
        for item in process.extract(query, possible_answers, limit=1, scorer=fuzz.token_set_ratio):
            if item[1] > 75:
                print(item)
                self.speak("Here is some Google result...")
                self.speak(item[0])
                status = True
                break
        return status

    def tryGoogle(self, query):
        searchResult = []
        for search_link in search(query, stop=5, pause=0.0):
            searchResult.append(search_link)
            if 'https://en.wikipedia.org/wiki' in search_link:
                query = search_link.replace("https://en.wikipedia.org/wiki", "")
                self.tryWiki(query)
                return True

        if len(searchResult) > 0:
            for link in searchResult:
                possible_answers = self.scrapWebPage(link)
                status = self.getBestResult(query, possible_answers)
                if status:
                    break

        return status

    def processQuery(self, query):
        if "stop" in query:
            self.speak("Ok! Bye")
            exit()
        else:
            clean_data = self.removePunctuation(query)
            token_list = self.getTokens(clean_data)

            clean_query = ""
            for word in self.removeStopWords(token_list):
                clean_query += word + " "

            if str(query).__contains__("who"):
                if not self.tryWiki(clean_query):
                    if not self.tryGoogle(clean_query):
                        context, top_headlines = self.tryNews(query)
                        self.speak(top_headlines)

            elif any(word in query for word in ["what", "where", "how"]):
                context, top_headlines = None, None
                print("Clean Query: ", clean_query)
                for word in clean_query.split():
                    if word not in words.words():
                        print("Word not in dictionary: ", word)
                        context, top_headlines =  self.tryNews(clean_query)
                        break
                
                if context and top_headlines:
                    context_query = query +" "+ context

                else:
                    context_query = query
                        
                print("Searching for: ", context_query)

                if not self.tryGoogle(context_query):
                    context, top_headlines =  self.tryNews(clean_query)
                    if context and top_headlines:
                        self.speak("I got realated news!")
                        self.speak(top_headlines['content'])
                    else:
                        self.speak("I am sorry! I do not understand")

            else:
                context, top_headlines =  self.tryNews(clean_query)
                self.speak("I got realated news!")
                self.speak(self.removePunctuation(top_headlines['content']))