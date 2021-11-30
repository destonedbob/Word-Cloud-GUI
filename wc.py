from PyQt5.QtWidgets import QApplication, QTabWidget
import wordcloud
import nltk
import pandas as pd
import string

def _preprocess(tokens, addedStopWords):
        res = [t for t in tokens if t not in string.punctuation]
        res = [t.lower() for t in res]
        res = [t for t in res if t not in nltk.corpus.stopwords.words('english') + [ "’", "“", "”","would", "could", '``', "''", "'s"] + addedStopWords]
        lemmatizer = nltk.WordNetLemmatizer()
        res = [lemmatizer.lemmatize(t) for t in res]
        return res 

try:
    df = pd.read_csv('test.csv')
except UnicodeDecodeError:
    df = pd.read_csv('test.csv', encoding='latin-1')

col = 'A super duper long very extra long A very very long column called Text'
col2 = 'A super duper long very extra long A very very long column called Column1'
text = ' '.join(entry for entry in df[col])
tokens = nltk.word_tokenize(text)
tokens_cleaned = _preprocess(tokens, [])
bigram = [' '.join(each) for each in list(nltk.bigrams(tokens_cleaned))]
trigram = [' '.join(each) for each in list(nltk.trigrams(tokens_cleaned))]
freq = nltk.FreqDist(tokens_cleaned+bigram+trigram)
res = pd.DataFrame(freq.items(),columns=['Word/Phrase', 'Count']).sort_values('Count', ascending=False).reset_index().drop('index', axis=1)
res

# from PyQt5.QtWidgets import QTabWidget, QWidget
# import sys
# app = QApplication(sys.argv)
# tabs = QTabWidget()
# right = QWidget()
# right2 = QWidget()
# tabs.addTab(right, 'Word Cloud')
# tabs.addTab(right2, 'Word Frequencies')
# sys.exit()

for each in res.iterrows():
    for i, v in enumerate(each[1]):
        print(i, v)
    break
import numpy as np
df[col].replace(0,np.nan).fillna('').astype(str)
df[col].dtype