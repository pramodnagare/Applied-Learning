import time
import spacy
from textblob import TextBlob

nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

black_list_characters = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

class PrepareText():

    def preprocessText(self, text):
        data = []
        for word in str(text).split(' '):
            if len(word) < 2 or word.startwith(('#', '@', 'http', 'www')):
                continue
            word = self.getLemmatze(word.lower())
            data.extend(word)
                

    def removePunctuation(self, query):
        query = str(query.encode('utf-8', 'ignore')).replace("b'", "")
        query = query.translate(str.maketrans('', '', black_list_characters))
        return query

    def getLemmatze(self, text):
        doc = nlp(text)
        token_list = []
        for token in doc:
            word = token.lemma_
            if word != '-PRON-':
                token_list.append(word)
        return token_list

    def removeStopWords(self, token_list):
        passed_words =[] 

        for word in token_list:
            lexeme = nlp.vocab[word]
            if lexeme.is_stop == False and word != " ":
                passed_words.append(word)
        
        return passed_words
