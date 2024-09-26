import random
import json
import requests
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
from transformers import pipeline

class ChatBot:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

        # Carregue os intents do arquivo JSON com a codificação UTF-8
        with open('intents.json', encoding='utf-8') as json_data:
            self.intents = json.load(json_data)

        # Carregue os intents do arquivo JSON com a codificação UTF-8
        self.intents = json.loads(open('intents.json', encoding='utf-8').read())
        self.medicamentos = json.loads(open('medicamentos.json', encoding='utf-8').read())
        self.palavras = pickle.load(open('palavras.pkl', 'rb'))
        self.classes = pickle.load(open('classes.pkl', 'rb'))
        self.model = load_model('chatbotmodel.h5')

    def get_estoque(self, medicamento):
        url = 'http://localhost:5000/api/medicamentos/id?nome_medicamento=' + medicamento

        response_id = requests.get(url)

        if response_id.status_code == 200:
            # Extrai o conteúdo JSON da resposta
            data = response_id.json()
            
            # Verifica se a resposta é uma tupla (provavelmente um dicionário e o status 200)
            if isinstance(data, tuple):
                # Pega o primeiro elemento da tupla (que deve ser o dicionário com 'id_medicamento')
                medicamento_data = data[0]
            else:
                # Se não for uma tupla, assume que data já é o dicionário esperado
                medicamento_data = data
    
        # Acessa o valor de 'id_medicamento' se ele estiver no dicionário
        medicamento_id = medicamento_data.get('id_medicamento')
            
        # Verifica se medicamento_id é válido antes de gerar a URL
        if medicamento_id:
            url_get_estoque = f'http://localhost:5000/api/estoque?medicamento_id={medicamento_id}'
            response_get_estoque = requests.get(url_get_estoque)
            
            if response_get_estoque.status_code == 200:
                data = response_get_estoque.json()
                return data
                
        return None

    def clean_up_sentence(self, sentence):
        sentence_words = nltk.tokenize.word_tokenize(sentence, language='portuguese')
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
    
    def identificar_intencao_com_ia(self, mensagem_usuario, intents):
        classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        labels = [intent['tag'] for intent in intents['intents']]
        result = classifier(mensagem_usuario, labels)
        return result['labels'][0]

    def get_response(self, message):
        ints = self.predict_class(message)
        try:
            tag_identificada = self.identificar_intencao_com_ia(message, self.medicamentos)

            if tag_identificada:
                resposta = self.get_estoque(tag_identificada)
                if resposta:
                    ints = self.predict_class(resposta)
            pass
        finally:
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
