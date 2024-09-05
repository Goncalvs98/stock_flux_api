import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
nltk.download('punkt')



class ChatBot:
    def __init__(self):
        nltk.data.path.clear() 
        nltk.download('punkt')
        nltk.download('wordnet')

        self.lemmatizer = WordNetLemmatizer()

        # Carregue os intents do arquivo JSON com a codificação UTF-8
        with open('intents.json', encoding='utf-8') as json_data:
            self.intents = json.load(json_data)

        # Carregue os intents do arquivo JSON com a codificação UTF-8
        self.intents = json.loads(open('intents.json', encoding='utf-8').read())
        self.palavras = pickle.load(open('palavras.pkl', 'rb'))
        self.classes = pickle.load(open('classes.pkl', 'rb'))
        self.model = load_model('chatbotmodel.h5')

    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence, language='portuguese')
        sentence_words = [self.lemmatizer.lemmatize(palavra.lower()) for palavra in sentence_words]
        return sentence_words

    def bag_of_words(self, sentence):
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0] * len(self.palavras)
        for w in sentence_words:
            for i, palavra in enumerate(self.palavras):
                if palavra == w:
                    bag[i] = 1
        return np.array(bag)

    def predict_class(self, sentence):
        bow = self.bag_of_words(sentence)
        res = self.model.predict(np.array([bow]))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({'intent': self.classes[r[0]], 'probability': str(r[1])})
        return return_list

    def get_response(self, message):
        ints = self.predict_class(message)
        res = self._get_response_from_intent(ints)
        return res

    def _get_response_from_intent(self, intents_list):
        if len(intents_list) == 0:
            return "Desculpe, não entendi isso."

        tag = intents_list[0]['intent']
        for i in self.intents['intents']:
            if i['tag'] == tag:
                result = random.choice(i['responses'])
                break
        return result
