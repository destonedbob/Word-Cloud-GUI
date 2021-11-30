import pandas as pd
import numpy as np
from pathlib import Path
import wordcloud
import nltk
import string

class Model():
    def __init__(self, controller):
        self.df = pd.DataFrame()
        self.controller = controller
        self.currentCol = ''
        self.addedStopWords = []
        self.wcObject = None
        self.freq = None
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
    
    def load_csv(self, csv_name):
        try:
            self.df = pd.read_csv(csv_name)
        except:
            try:
                self.df = pd.read_csv(csv_name, encoding='iso-8859-1')
            except:
                self.df = pd.read_csv(csv_name, encoding='latin-1')
        self.controller.columns = self.df.columns.tolist()

    def _preprocess(self, tokens, addedStopWords):
        res = [t for t in tokens if t not in string.punctuation]
        res = [t.lower() for t in res]
        res = [t for t in res if t not in nltk.corpus.stopwords.words('english') + [ "’", "“", "”","would", "could", '``', "''", "'s", '...'] + addedStopWords]
        lemmatizer = nltk.WordNetLemmatizer()
        res = [lemmatizer.lemmatize(t) for t in res]
        return res 

    def createWCObject(self, addedStopWords):
        self.addedStopWords = addedStopWords
        colofText = self.df[self.currentCol].fillna('').astype(str)
        text = ' '.join(entry for entry in colofText)
        tokens = nltk.word_tokenize(text)
        tokens_cleaned = self._preprocess(tokens, self.addedStopWords)
        bigram = [' '.join(each) for each in list(nltk.bigrams(tokens_cleaned))]
        trigram = [' '.join(each) for each in list(nltk.trigrams(tokens_cleaned))]
        self.freq = nltk.FreqDist(tokens_cleaned+bigram+trigram)
        self.freq_df = pd.DataFrame(self.freq.items(),columns=['Word/Phrase', 'Count']).sort_values('Count', ascending=False).reset_index().drop('index', axis=1)
        self.wcObject = wordcloud.WordCloud(background_color="black").generate_from_frequencies(self.freq)
