import json
import requests
from datetime import datetime
from nltk.stem import WordNetLemmatizer
from difflib import get_close_matches  # Para identificar a intenção de forma simples com similaridade

class ChatBot:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

        # Carregue os intents e medicamentos do arquivo JSON com a codificação UTF-8
        with open('intents.json', encoding='utf-8') as json_data:
            self.intents = json.load(json_data)
        with open('medicamentos.json', encoding='utf-8') as json_data:
            self.medicamentos = json.load(json_data)

    def get_estoque(self, medicamento):
        url = 'http://localhost:5000/api/medicamentos/id?nome_medicamento=' + medicamento
        response_id = requests.get(url)

        if response_id.status_code == 200:
            data = response_id.json()
            
            if isinstance(data, list) and len(data) > 0:
                medicamento_data = data[0]
            elif isinstance(data, dict):
                medicamento_data = data
            else:
                return None
    
        medicamento_id = medicamento_data.get('id_medicamento')
        
        if medicamento_id:
            url_get_estoque = f'http://localhost:5000/api/estoque?medicamento_id={medicamento_id}'
            response_get_estoque = requests.get(url_get_estoque)
            
            if response_get_estoque.status_code == 200:
                data = response_get_estoque.json()
                return data
                
        return None

    def identificar_intencao(self, mensagem_usuario, intents):
        # Extrai as tags das intenções do JSON
        tags = [intent['tag'] for intent in intents['intents']]
        
        # Busca a intenção mais próxima da mensagem do usuário usando similaridade
        tag_encontrada = get_close_matches(mensagem_usuario, tags, n=1, cutoff=0.6)
        
        return tag_encontrada[0] if tag_encontrada else None

    def get_response(self, message):
        try:
            # Identifica a intenção com base na mensagem do usuário
            tag_identificada = self.identificar_intencao(message, self.medicamentos)

            if tag_identificada:
                resposta = self.get_estoque(tag_identificada)

                if resposta:
                    if isinstance(resposta, list) and len(resposta) > 0:
                        mensagem = f"Informações sobre o medicamento {tag_identificada}:\n\n"
                        
                        for item in resposta:
                            medicamento_nome = item.get('Medicamento', 'Nome não especificado')
                            responsavel_nome = item.get('Responsável', 'Responsável não especificado')
                            tipo_descricao = item.get('Tipo Movimentação', 'Descrição não especificada')
                            quantidade = item.get('Quantidade', 'Quantidade não especificada')
                            data = item.get('Data', 'Data não especificada')
                            motivo = item.get('Motivo', 'Não especificado')

                            # Formatar a data se ela existir
                            if data != 'Data não especificada':
                                data_formatada = datetime.strptime(data, '%Y-%m-%dT%H:%M:%S').strftime('%d de %B de %Y')
                            else:
                                data_formatada = data

                            # Montando a mensagem formatada
                            mensagem += (
                                f"  Medicamento: {medicamento_nome}\n"
                                f"  Responsável/Local: {responsavel_nome}\n"
                                f"  Tipo/Descrição: {tipo_descricao}\n"
                                f"  Quantidade: {quantidade}\n"
                                f"  Data: {data_formatada}\n"
                                f"  Motivo: {motivo}\n"
                                "------------------------------\n\n"
                            )
                        
                        return mensagem
                    
                    else:
                        return f"Não foi possível encontrar informações sobre o medicamento {tag_identificada}."
            
        except Exception as e:
            print(f"Erro ao processar a mensagem: {e}")
        
        return 0
