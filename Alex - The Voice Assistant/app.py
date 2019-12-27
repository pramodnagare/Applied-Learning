from googlesearch import search
from bs4 import BeautifulSoup
import requests as req
from newsapi import NewsApiClient
from nltk.corpus import words
import pyttsx3
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import speech_recognition as sr
from spacy.lang.en import English
import string
import spacy
import datetime
import wikipedia
import time
from threading import Thread

newsapi = NewsApiClient(api_key="")

nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

black_list_characters = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning!")

    elif hour>=12 and hour<18:
        speak("Good Afternoon!")   

    else:
        speak("Good Evening!")  

    speak("Hi There!. Please tell me how may I help you")

def speak(audio):
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.say(audio)
    engine.runAndWait()

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        # r.pause_threshold = 0.5
        audio = r.listen(source)

    try:
        print("Recognizing...")    
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        # print(e)    
        print("Say that again please...")  
        return None
    return query

def removePunctuation(query):
    query = str(query.encode('utf-8', 'ignore')).replace("b'", "")
    query = query.translate(str.maketrans('', '', black_list_characters))
    return query

def getTokens(text):
    doc = nlp(text)
    token_list = []
    for token in doc:
        word = token.lemma_
        if word != '-PRON-':
            token_list.append(word)
    return token_list

def removeStopWords(token_list):
    passed_words =[] 

    for word in token_list:
        lexeme = nlp.vocab[word]
        if lexeme.is_stop == False and word != " ":
            passed_words.append(word)
    
    return passed_words

def getTopWords(total_content, query):
    
    token_list = getTokens(total_content)

    passed_words = removeStopWords(token_list)

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

def tryWiki(query):
    try:
        results = wikipedia.summary(query, sentences=10)
        results = results.replace("\n", " ").split(". ")
        speak("According to Wikipedia")
        speak(results[0:2])
        
        for item in process.extract(query, results[2:], limit=1):
            print(item)
            speak(item[0])
        return True

    except Exception as e:
        return False

def tryNews(query):
    if query and query != "":
        top_headlines = newsapi.get_everything(q=query, language='en', from_param='2019-20-12', to='2019-25-12', sort_by='relevancy')

        if len(top_headlines['articles']) >= 2:
            total_content = ""
            for news in top_headlines['articles']:
                if "content" in news.keys():
                    total_content += str(news['content']).lower()
            total_content = removePunctuation(total_content)
            top_words = getTopWords(total_content, query)

            context = ""
            for item in top_words:
                context += item[0] +" "
            
            return context, top_headlines['articles'][0]
    
    return None, None

def scrapWebPage(url):
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

def getBestResult(possible_answers):
    status = False
    for item in process.extract(query, possible_answers, limit=1, scorer=fuzz.token_set_ratio):
        if item[1] > 75:
            print(item)
            speak("Here is some Google result...")
            speak(item[0])
            status = True
            break
    return status

def tryGoogle(query):
    searchResult = []
    for search_link in search(query, stop=5, pause=0.0):
        searchResult.append(search_link)
        if 'https://en.wikipedia.org/wiki' in search_link:
            query = search_link.replace("https://en.wikipedia.org/wiki", "")
            tryWiki(query)
            return True

    if len(searchResult) > 0:
        for link in searchResult:
            possible_answers = scrapWebPage(link)
            status = getBestResult(possible_answers)
            if status:
                break

    return status

def processQuery(query):
    if "stop" in query:
            speak("Ok! Bye")
            exit()
    else:
        clean_data = removePunctuation(query)
        token_list = getTokens(clean_data)

        clean_query = ""
        for word in removeStopWords(token_list):
            clean_query += word + " "

        if str(query).__contains__("who"):
            if not tryWiki(clean_query):
                if not tryGoogle(clean_query):
                    context, top_headlines = tryNews(query)
                    speak(top_headlines)

        elif any(word in query for word in ["what", "where", "how"]):
            context, top_headlines = None, None
            print("Clean Query: ", clean_query)
            for word in clean_query.split():
                if word not in words.words():
                    print("Word not in dictionary: ", word)
                    context, top_headlines =  tryNews(clean_query)
                    break
            
            if context and top_headlines:
                context_query = query +" "+ context

            else:
                context_query = query
                    
            print("Searching for: ", context_query)

            if not tryGoogle(context_query):
                context, top_headlines =  tryNews(clean_query)
                if context and top_headlines:
                    speak("I got realated news!")
                    speak(top_headlines['content'])
                else:
                    speak("I am sorry! I do not understand")

        else:
            context, top_headlines =  tryNews(clean_query)
            speak("I got realated news!")
            speak(removePunctuation(top_headlines['content']))

if __name__ == "__main__":
    while True:
        query = takeCommand()

        if query and "alex stop" in query.lower():
            speak("OK Bye!")
            exit()
        
        elif query:
            query = str(query).lower()
            if query.startswith("alex"):
                query = query.replace("alex", "")
                processQuery(query)