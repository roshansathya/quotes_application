import nltk
from nltk.corpus import wordnet, stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
VERB_CODES = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}

def process_quote(quote):
    processed_words = {}
    words_list = word_tokenize(quote)
    tags = nltk.pos_tag(words_list)
    for i, word in enumerate(words_list):
        word = word.lower()
        if word in stop_words or len(word) <= 3:
            continue

        for syn in wordnet.synsets(word): 
            for l in syn.lemmas():
                processed_words[word] = processed_words.get(word, 0) + 1

        if tags[i][1] in VERB_CODES:  
            lemmatized = lemmatizer.lemmatize(word, 'v')
        else: 
            lemmatized = lemmatizer.lemmatize(word) 

        processed_words[word] = processed_words.get(word, 0) + 1
    return ' '.join(list(processed_words.keys()))
