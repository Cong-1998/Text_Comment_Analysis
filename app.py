# import libraries
import streamlit as st
import malaya
import re
import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
nltk.download('punkt')
from wordcloud import WordCloud
import gensim
from gensim import corpora, models
from streamlit_tags import st_tags, st_tags_sidebar
from streamlit_player import st_player
from Topic.gsdmm import MovieGroupProcess
from Topic.topic import processing
from Topic.topic import token
from Topic.topic import topic_model
from Topic.topic import top_words
from Topic.topic import create_topics_dataframe
from Topic.topic import create_WordCloud
from Language.language import detect_lang
from Sentiment.sentiment import detect_sentiment
from Emotion.emotion import detect_emotion

# table of content
class Toc:
    def __init__(self):
        self._items = []
        self._placeholder = None
    
    def title(self, text):
        self._markdown(text, "h1")

    def header(self, text):
        self._markdown(text, "h2", " " * 2)

    def subheader(self, text):
        self._markdown(text, "h3", " " * 4)

    def placeholder(self, sidebar=True):
        self._placeholder = st.sidebar.empty() if sidebar else st.empty()

    def generate(self):
        if self._placeholder:
            self._placeholder.markdown("\n".join(self._items), unsafe_allow_html=True)
    
    def _markdown(self, text, level, space=""):
        key = "-".join(text.split()).lower()
        st.markdown(f"<{level} id='{key}'>{text}</{level}>", unsafe_allow_html=True)
        self._items.append(f"{space}* <a href='#{key}'>{text}</a>")

# hide menu bar
st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)
    
# set up layout
padding = 1
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)

# set up title
st.title("Comment Analysis")
st.write('\n')

# set up sidebar
st.sidebar.header("Table of Content")
toc = Toc()
toc.placeholder()

# why using
st.write("Why using [this app](#why-using-this-app)❓")

# upload file
toc.header("Upload csv file")
file_upload = st.file_uploader("", type=["csv"])
if file_upload is not None:
    data = pd.read_csv(file_upload, encoding='unicode_escape')
    st.write(data)
    name = file_upload.name.replace('.csv', '')
    name = name+"_labelled.csv"

# select cluster
toc.header("Select the number of clusters")
int_val = st.number_input('', min_value=1, max_value=30, value=5, step=1)

# add stopword
list_stop = []
my_expander = st.expander(label='Advanced Setting')
with my_expander:
    st.write("This tab is to remove stopwords.")
    st.subheader("[What is stopwords](#stopwords) :question:")
    keywords = st_tags(
        label='Enter Stopwords: :point_down:',
        text='Press enter to add more',
        value=[],
        key="aljnf")
    st.write(keywords)
    st.write("*Don't collapse this tab.")
list_stop = keywords

# run the program
result = st.button("Run")
if result:
    wc = []
    ans = []
    st.write("Be patient, need to wait 3 to 9 minutes :smile:")
    st.write("If raising error, please reduce the number of clusters")

    # Topic clustering
    wc, ans, topic_df = processing(data, gensim, word_tokenize, np, MovieGroupProcess, pd, WordCloud, int_val, list_stop)

    # Detect language
    topic_df['Language'] = topic_df['comment'].apply(detect_lang)

    # Detect sentiment
    sentiment_df = detect_sentiment(topic_df, malaya)

    # Detect emotion
    final_df = detect_emotion(sentiment_df)
    
    # download labelled file
    st.write("Below is the labelled file, click button to download.")
    csv = final_df.to_csv(index=False)
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name=name,
        mime='text/csv',
    )
    st.write('\n')
    
    st.write(ans)
    for i in range(len(wc)):
        st.markdown('Most used words in type '+str(i+1))
        st.image(wc[i].to_image())
        st.write('\n')
st.write('\n')

# how to use
toc.header("How to Use")
st.write("1. Please upload csv file and make sure your data are in first column.")
st.write("*How to convert excel file to [csv file](#csv-file).")
st.write("2. Option: You can expand Advanced Setting tab to add new [stopword](#stopwords).")
st.write("3. Please select the number of clusters.")
st.write("4. Please click the 'Run' button.")
st.write('\n')

# how to covert excel to csv
st.subheader("CSV file")
st.write('This video will teach you how to convert excel file to csv file.')
# Embed a youtube video
st_player("https://www.youtube.com/watch?v=IBbJzzj5r90")
st.write('\n')

# stopword
st.subheader("Stopwords")
st.write("Stopwords are the words which does not add much meaning to a sentence. They can safely be ignored without sacrificing the meaning of the sentence. For example, the words like ada, apa, dia, a, an, the etc.")
st.write("*Here are [stopwords](https://github.com/Cong-1998/Text_Comment_Analysis/blob/main/stopwords.txt). :point_left:")

# functions
toc.header("Why Using This App")
st.write(
    """    
- **Clustering of social media comments.**
- **To determine sentiment of comments.**
- **To analyze the underlying emotions expressed based on comments.**
    """)

toc.generate()
