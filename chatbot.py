import json
import random
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib  # Para correção ortográfica

class ChatBot:
    def __init__(self):
        # Carregar intents e dados de medicamentos
        with open('stockfluxIA1/stock_flux_api/medicamento.json', encoding='utf-8') as json_data:
            self.intents = json.load(json_data)

        # Extrair padrões (patterns) e tags (medicamentos)
        self.padroes = []
        self.tags = []
        for intent in self.intents['intents']:
            for padrao in intent['patterns']:
                self.padroes.append(padrao.lower())  # Padrões de frases
                self.tags.append(intent['tag'])  # Tags correspondentes (nomes de medicamentos)

        # Vetorizar os padrões (Bag of Words ou TF-IDF)
        self.vetorizador = CountVectorizer().fit(self.padroes)

    def corrigir_ortografia(self, mensagem):
        """Corrige palavras na mensagem do usuário usando os padrões como referência."""
        palavras_na_mensagem = mensagem.lower().split()
        todas_palavras_padroes = set(" ".join(self.padroes).split())

        palavras_corrigidas = []
        for palavra in palavras_na_mensagem:
            palavras_similares = difflib.get_close_matches(palavra, todas_palavras_padroes, n=1, cutoff=0.8)
            if palavras_similares:
                palavras_corrigidas.append(palavras_similares[0])  # Usa a palavra mais próxima
            else:
                palavras_corrigidas.append(palavra)  # Mantém a palavra original se não houver correspondência
        return " ".join(palavras_corrigidas)

    def encontrar_intencao(self, mensagem):
        """Encontra a intenção (medicamento) com base na similaridade de cosseno."""
        # Corrigir a ortografia da mensagem
        mensagem_corrigida = self.corrigir_ortografia(mensagem)
        print(f"Mensagem corrigida: {mensagem_corrigida}")

        # Vetorizar a mensagem corrigida
        vetor_mensagem = self.vetorizador.transform([mensagem_corrigida])
        vetor_padroes = self.vetorizador.transform(self.padroes)

        # Calcular a similaridade de cosseno entre a entrada do usuário e os padrões
        similaridades = cosine_similarity(vetor_mensagem, vetor_padroes)

        # Encontrar o padrão mais similar
        indice_melhor_correspondencia = similaridades.argmax()  # Índice do padrão mais próximo
        pontuacao_melhor_correspondencia = similaridades[0, indice_melhor_correspondencia]  # Pontuação de similaridade

        # Se a similaridade for alta o suficiente (ex: 0.5), consideramos um match
        if pontuacao_melhor_correspondencia > 0.5:
            return self.tags[indice_melhor_correspondencia]  # Retorna a tag do medicamento correspondente
        return None  # Se nenhuma correspondência foi encontrada

    def obter_resposta(self, mensagem):
        """Retorna uma resposta com base no medicamento identificado."""
        intencao = self.encontrar_intencao(mensagem)
        if intencao:
            for dados_intencao in self.intents['intents']:
                if dados_intencao['tag'] == intencao:
                    # Corrigir a resposta para oxcarbazepina descontinuada
                    if intencao == 'Oxcarbazepina':
                        return random.choice(dados_intencao['responses'])  # Seleciona uma resposta aleatória da lista
                    else:
                        return f"O estoque de {intencao} está disponível."  # Resposta padrão para medicamentos disponíveis
        return "Desculpe, não entendi sua pergunta."

    def teste_manual(self):
        """Inicia um loop para interação com o usuário."""
        while True:
            entrada_usuario = input("Faça uma pergunta sobre medicamentos (ou digite 'sair' para encerrar): ")
            if entrada_usuario.lower() == 'sair':
                break

            resposta = self.obter_resposta(entrada_usuario)
            print(f"Resposta do chatbot: {resposta} \n")

if __name__ == "__main__":
    bot = ChatBot()
    bot.teste_manual()
