from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import oracledb
import json
from chatbot import ChatBot  # Importa a classe ChatBot

app = Flask(__name__)
api = Api(app, version='1.0', title='API StockFlux',
          description='Uma API para gerenciar os dados do dashboard',
          doc='/docs'  # URL para o Swagger UI
          )
CORS(app)

ns = api.namespace('api', description='Operações relacionadas às tabelas')

api.add_namespace(ns)

# Instancia o chatbot
bot = ChatBot()

medicamento_model = api.model('Medicamento', {
    'Categoria': fields.String(required=True, description='Categoria do medicamento'),
    'Motivo': fields.String(required=False, description='Motivo do medicamento'),
    'Nome': fields.String(required=True, description='Nome do medicamento'),
    'Código': fields.String(required=True, description='Código do medicamento'),
    'Quantidade Minima': fields.Integer(required=True, description='Quantidade mínima do medicamento'),
    'Localização': fields.String(required=True, description='Localização do medicamento'),
    'Status': fields.String(required=True, description='Status do medicamento')
})

status_model = api.model('Status',{
    'Id': fields.Integer(required=True, description='Id do status'),
    'Descrição': fields.String(required=True, description='Descrição do status'),
    'Motivo': fields.String(required=True, description='Motivo do status'),
})

fornecedores_model = api.model('Fornecedores',{
    "Id": fields.Integer(required=True, description='Id do fornecedor'),
    "Nome": fields.String(required=True, description='Nome do fornecedor'),
    "Telefone": fields.String(required=True, description='Telefone do fornecedor'),
    "Email": fields.String(required=True, description='Email do fornecedor'),
})

materiais_model = api.model('Materiais',{
    "Id": fields.Integer(required=True, description='Id do material'),
    "Fornecedor": fields.String(required=True, description='fornecedor do material'),
    "Descrição": fields.String(required=True, description='Descrição do material'),
})

categorias_model = api.model('Categorias',{
    "Id": fields.Integer(required=True, description='Id da categoria'),
    "Descrição": fields.String(required=True, description='Descrição da categoria'),
})

motivos_model = api.model('Motivos',{
    "Id": fields.Integer(required=True, description='Id do motivo'),
    "Descrição": fields.String(required=True, description='Descrição do motivo'),
})

cargos_model = api.model('Cargos',{
    "Id": fields.Integer(required=True, description='Id do cargo'),
    "Descrição": fields.String(required=True, description='Descrição do cargo'),
})

departamentos_model = api.model('Departamentos',{
    "Id": fields.Integer(required=True, description='Id do departamento'),
    "Descrição": fields.String(required=True, description='Descrição do departamento'),
})

estoque_model = api.model('Estoque',{
    "Id": fields.Integer(required=True, description='Id do estoque'),
    "Medicamento": fields.String(required=True, description='Medicamento do estoque'),
    "Responsável": fields.String(required=True, description='Responsável do estoque'),
    "Tipo Movimentação": fields.String(required=True, description='Tipo de Movimentação do estoque'),
    "Quantidade": fields.Integer(required=True, description='Quantidade do estoque'),
    "Data": fields.DateTime(required=True, description='Data do estoque'),
    "Motivo": fields.String(required=True, description='Motivo do estoque'),
})

etapas_producao_model = api.model('Etapas_Producao',{
    "Id": fields.Integer(required=True, description='Id da etapa da produção'),
    "Descrição": fields.String(required=True, description='Descrição da etapa da produção'),
    "Prazo Estimado": fields.Integer(required=True, description='Prazo Estimado da etapa da produção'),
})

producao_model = api.model('Producao',{
    "Id": fields.Integer(required=True, description='Id da produção'),
    "Medicamento": fields.String(required=True, description='Medicamento da produção'),
    "Etapa": fields.String(required=True, description='Etapa da produção'),
    "Data Início": fields.DateTime(required=True, description='Data Início da produção'),
    "Data Fim Prevista": fields.DateTime(required=True, description='Data Fim Prevista da produção'),
    "Data Fim Real": fields.DateTime(required=True, description='Data Fim Real da produção'),
})

entradas_previstas_model = api.model('EntradasPrevistas',{
    "Id": fields.Integer(required=True, description='Id da entrada prevista'),
    "Material": fields.String(required=True, description='Material da entrada prevista'),
    "Medicamento": fields.String(required=True, description='Descrição da entrada prevista'),
    "Quantidade": fields.Integer(required=True, description='Quantidade da entrada prevista'),
    "Data Prevista": fields.DateTime(required=True, description='Data Prevista da entrada prevista'),
})

atrasos_producao_model = api.model('AtrasosProducao',{
    "Id": fields.Integer(required=True, description='Id do atraso'),
    "Medicamento": fields.String(required=True, description='Medicamento da produção em atraso'),
    "Etapa": fields.String(required=True, description='etapa da produção em atraso'),
    "Dias de Atraso": fields.Integer(required=True, description='Dias de Atraso'),
    "Motivo": fields.String(required=True, description='Motivo do atraso'),
})

chat_message_model = ns.model('ChatMessage', {
    'message': fields.String(required=True, description='A mensagem do usuário')
})

def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)

def get_db_connection():
    credentials = load_credentials()
    connection = oracledb.connect(user=credentials['user'], password=credentials['password'], dsn=credentials['dsn'])
    return connection

# Medicamentos
@ns.route('/medicamentos/id')
class MedicamentoIDResource(Resource):
    @ns.doc('get_medicamento_id')
    def get(self):
        # Obter o nome do medicamento a partir dos parâmetros da URL
        nome_medicamento = request.args.get('nome_medicamento')

        # Garantir que o nome do medicamento foi fornecido
        if not nome_medicamento or not isinstance(nome_medicamento, str) or nome_medicamento.strip() == '':
            return {'error': 'O nome do medicamento é obrigatório e deve ser uma string válida.'}, 400

        try:
            # Conectar ao banco de dados com context manager
            with get_db_connection() as connection:
                cursor = connection.cursor()

                # Definir a query SQL para buscar o id_medicamento
                query = """
                    SELECT id_medicamento
                    FROM rm93069.medicamento
                    WHERE nome = :nome_medicamento
                """

                # Executar a query com o nome do medicamento como parâmetro
                cursor.execute(query, {"nome_medicamento": nome_medicamento})

                # Obter o resultado da consulta
                row = cursor.fetchone()

                # Verificar se o medicamento foi encontrado
                if row:
                    medicamento_id = {"id_medicamento": row[0]}, 200
                else:
                    medicamento_id = {"error": "Medicamento não encontrado"}, 404


        except Exception as e:
            # Retornar uma mensagem de erro se algo der errado
            return {'error': f'Ocorreu um erro ao processar a solicitação: {str(e)}'}, 500

        # Retornar o resultado
        return medicamento_id

# Medicamentos
@ns.route('/medicamentos')
class MedicamentoResource(Resource):
    @ns.doc('list_medicamentos')
    @ns.marshal_list_with(medicamento_model)
    def get(self):
        categoria = request.args.get('categoria_id')
        motivo = request.args.get('motivo_id')
        status = request.args.get('status_id')
        medicamento = request.args.get('medicamento_nome')

        connection = get_db_connection()
        cursor = connection.cursor()

        # Preparar a consulta para chamar a função e retornar o SYS_REFCURSOR
        query = """
            BEGIN
                :ref_cursor := get_medicamentos(:categoria, :motivo, :status, :medicamento);
            END;
        """
    
        # Criação de um cursor de referência para armazenar o resultado
        ref_cursor = cursor.var(oracledb.CURSOR)

        # Executar a consulta passando os parâmetros necessários
        cursor.execute(query, {
            "ref_cursor": ref_cursor,
            "categoria": categoria,
            "motivo": motivo,
            "status": status,
            "medicamento": medicamento
        })

        # Obter os resultados do cursor retornado
        rows = ref_cursor.getvalue().fetchall()

        if not rows:
            return {"error": "Nenhum medicamento encontrado"}, 404

        medicamentos = []
        for row in rows:
            medicamento = {
                "Categoria": row[0],
                "Motivo": row[1],
                "Nome": row[2],
                "Código": row[3],
                "Quantidade Minima": row[4],
                "Localização": row[5],
                "Status": row[6],
            }
            medicamentos.append(medicamento)

            # Verifica se o medicamento foi descontinuado (por exemplo, pelo status)
            if row[6] == 'Descontinuado':  # Suponha que 'Status' esteja na posição 6
                nome = row[2]  # Nome do medicamento
                dosagem = row[4]  # Quantidade mínima (adaptar se necessário)
                fabricante = "Fabricante"  # Você pode obter essa informação de outra tabela, se necessário
                data_discontinuacao = "Data aqui"  # Obtenha essa informação de uma coluna se disponível

                # Função para gerar o comunicado
                def gerar_comunicado(nome, dosagem, fabricante, data_discontinuacao):
                    comunicado = f"""
                    Comunicado sobre a descontinuação definitiva da fabricação/importação do medicamento {nome} {dosagem} mg
                    
                    São Paulo, {data_discontinuacao} — Em compromisso com a transparência junto aos pacientes e profissionais de saúde, a {fabricante} informa que o medicamento {nome}, na dosagem de {dosagem} mg será descontinuado definitivamente. Este produto não será mais comercializado pela {fabricante}.

                    Destacamos que a descontinuação se refere à dosagem de {dosagem} mg, sem impactar outras apresentações do medicamento, que estão sendo comercializadas normalmente.

                    Orientamos que pacientes e médicos conversem sobre a melhor conduta para a continuidade do tratamento.
                    
                    A Agência Nacional de Vigilância Sanitária (ANVISA) foi comunicada sobre essa situação conforme requerido na legislação vigente.

                    Para mais informações, estamos à disposição por meio do Serviço de Atendimento ao Consumidor pelo telefone 0800-XXX-XXXX ou através do site {fabricante}/fale-conosco.

                    Atenciosamente,

                    {fabricante}
                    """
                    return comunicado

                comunicado = gerar_comunicado(nome, dosagem, fabricante, data_discontinuacao)
                cursor.close()
                connection.close()

                # Retornar o comunicado como resposta
                return {"comunicado": comunicado}, 200

        # Fechar o cursor e a conexão se não for encontrado nenhum medicamento descontinuado
        cursor.close()
        connection.close()
        return medicamentos


# Status
@ns.route('/status')
class StatusResource(Resource):
    @ns.doc('list_status')
    @ns.marshal_list_with(status_model)
    def get(self):
        status = request.args.get('status_id')

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            BEGIN
                :ref_cursor := get_status(:status);
            END;
        """

        ref_cursor = cursor.var(oracledb.CURSOR)

        cursor.execute(query, {
            "ref_cursor": ref_cursor,
            "status": status,
        })

        rows = ref_cursor.getvalue().fetchall()

        status_list = []
        for row in rows:
            status_item = {
                "Id": row[0],
                "Descrição": row[1],
                "Motivo": row[2],
            }
            status_list.append(status_item)

        cursor.close()
        connection.close()
        return status_list

    @ns.doc('create_status')
    @ns.expect(status_model)
    def post(self):
        data = ns.payload  # Captura os dados enviados no corpo da requisição
        connection = get_db_connection()
        cursor = connection.cursor()

        sql_insert = """INSERT INTO rm93069.status (id_status, descricao, motivo) 
                            VALUES (:1, :2, :3)"""
        cursor.execute(sql_insert, (data['Id'], data['Descrição'], data['Motivo']))

        connection.commit()  # Confirma a transação

        cursor.close()
        connection.close()

        return {'message': 'Status inserido com sucesso!'}, 201

    @ns.doc('update_status')
    @ns.expect(status_model)
    def put(self):
        data = ns.payload  # Captura os dados enviados no corpo da requisição
        connection = get_db_connection()
        cursor = connection.cursor()

        sql_update = """UPDATE rm93069.status
                            SET descricao = :1, motivo = :2 
                            WHERE id_status = :3"""
        cursor.execute(sql_update, (data['Descrição'], data['Motivo'], data['Id']))

        connection.commit()  # Confirma a transação

        cursor.close()
        connection.close()

        return {'message': 'Status atualizado com sucesso!'}

    @ns.doc('delete_status')
    def delete(self):
        data = ns.payload  # Captura os dados enviados no corpo da requisição
        connection = get_db_connection()
        cursor = connection.cursor()

        sql_delete = "DELETE FROM rm93069.status WHERE id_status = :1"
        cursor.execute(sql_delete, (data['Id'],))

        connection.commit()  # Confirma a transação

        cursor.close()
        connection.close()

        return {'message': 'Status deletado com sucesso!'}

# Fornecedores
@ns.route('/fornecedores')
class FornecedorResource(Resource):
    @ns.doc('list_fornecedores')
    @ns.marshal_list_with(fornecedores_model)
    def get(self):
        fornecedor = request.args.get('fornecedor_id')

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            BEGIN
                :ref_cursor := get_fornecedores(:fornecedor);
            END;
        """

        # Criação da variável para armazenar o cursor de referência
        ref_cursor = cursor.var(oracledb.CURSOR)

        cursor.execute(query, {
            "ref_cursor": ref_cursor,
            "fornecedor": fornecedor,
        })

        # Agora, usamos o cursor da variável ref_cursor
        result_cursor = ref_cursor.getvalue()

        # Fetchall no cursor resultante da execução da função PL/SQL
        rows = result_cursor.fetchall()

        fornecedores = []
        for row in rows:
            fornecedor = {
                "Id": row[0],
                "Nome": row[1],
                "Telefone": row[2],
                "Email": row[3],
            }
            fornecedores.append(fornecedor)

        cursor.close()
        connection.close()
        return fornecedores

    @ns.doc('create_fornecedores')
    @ns.expect(fornecedores_model)
    def post(self):
        data = ns.payload  # Captura os dados enviados no corpo da requisição
        connection = get_db_connection()
        cursor = connection.cursor()

        sql_insert = """INSERT INTO rm93069.fornecedores (id_fornecedor, nome, telefone, email) 
                            VALUES (:1, :2, :3, :4)"""
        cursor.execute(sql_insert, (data['Id'], data['Nome'], data['Telefone'], data['Email']))

        connection.commit()  # Confirma a transação

        cursor.close()
        connection.close()

        return {'message': 'Status inserido com sucesso!'}, 201

    @ns.doc('update_fornecedores')
    @ns.expect(fornecedores_model)
    def put(self):
        data = ns.payload  # Captura os dados enviados no corpo da requisição
        connection = get_db_connection()
        cursor = connection.cursor()

        sql_update = """UPDATE rm93069.fornecedores
                            SET nome = :1, telefone = :2,  email = :3
                            WHERE id_fornecedor = :4"""
        cursor.execute(sql_update, (data['Nome'], data['Telefone'], data['Email'], data['Id']))

        connection.commit()  # Confirma a transação

        cursor.close()
        connection.close()

        return {'message': 'Status atualizado com sucesso!'}

    @ns.doc('delete_fornecedores')
    def delete(self):
        data = ns.payload  # Captura os dados enviados no corpo da requisição
        connection = get_db_connection()
        cursor = connection.cursor()

        sql_delete = "DELETE FROM rm93069.fornecedores WHERE id_fornecedor = :1"
        cursor.execute(sql_delete, (data['Id'],))

        connection.commit()  # Confirma a transação

        cursor.close()
        connection.close()

        return {'message': 'Status deletado com sucesso!'}

# Materiais
@ns.route('/materiais')
class MaterialResource(Resource):
    @ns.doc('list_materiais')
    @ns.marshal_list_with(materiais_model)
    def get(self):
        fornecedor = request.args.get('fornecedor_id')
        material = request.args.get('material_id')

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            BEGIN
                :ref_cursor := get_materiais(:material, :fornecedor);
            END;
        """

        ref_cursor = cursor.var(oracledb.CURSOR)

        cursor.execute(query, {
            "ref_cursor": ref_cursor,
            "material": material,
            "fornecedor": fornecedor,
        })

        result_cursor = ref_cursor.getvalue()

        rows = result_cursor.fetchall()

        materiais = []
        for row in rows:
            material = {
                "Id": row[0],
                "Fornecedor": row[1],
                "Descrição": row[2],
            }
            materiais.append(material)

        cursor.close()
        connection.close()
        return materiais

    @ns.doc('create_materiais')
    @ns.expect(materiais_model)
    def post(self):
        data = ns.payload  # Captura os dados enviados no corpo da requisição
        connection = get_db_connection()
        cursor = connection.cursor()

        sql_insert = """INSERT INTO rm93069.materiais (id_material, id_fornecedor, descricao) 
                                VALUES (:1, :2, :3)"""
        cursor.execute(sql_insert, (data['Id'], data['Id_Fornecedor'], data['Descricao']))

        connection.commit()  # Confirma a transação

        cursor.close()
        connection.close()

        return {'message': 'Status inserido com sucesso!'}, 201

    @ns.doc('update_materiais')
    @ns.expect(materiais_model)
    def put(self):
        data = ns.payload  # Captura os dados enviados no corpo da requisição
        connection = get_db_connection()
        cursor = connection.cursor()

        sql_update = """UPDATE rm93069.materiais
                                SET id_fornecedor = :2,  descricao = :3
                                WHERE id_material = :1"""
        cursor.execute(sql_update, (data['Id'], data['Id_Fornecedor'], data['Descricao'],))

        connection.commit()  # Confirma a transação

        cursor.close()
        connection.close()

        return {'message': 'Status atualizado com sucesso!'}

    @ns.doc('delete_materiais')
    def delete(self):
        data = ns.payload  # Captura os dados enviados no corpo da requisição
        connection = get_db_connection()
        cursor = connection.cursor()

        sql_delete = "DELETE FROM rm93069.materiais WHERE id_material = :1"
        cursor.execute(sql_delete, (data['Id'],))

        connection.commit()  # Confirma a transação

        cursor.close()
        connection.close()

        return {'message': 'Status deletado com sucesso!'}

# Categorias
@ns.route('/categorias')
class CategoriaResource(Resource):
    @ns.doc('list_categoria')
    @ns.marshal_list_with(categorias_model)
    def get(self):
        categoria = request.args.get('categoria_id')

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            BEGIN
                :ref_cursor := get_categorias(:categoria);
            END;
        """

        ref_cursor = cursor.var(oracledb.CURSOR)

        cursor.execute(query, {
            "ref_cursor": ref_cursor,
            "categoria": categoria,
        })

        result_cursor = ref_cursor.getvalue()

        rows = result_cursor.fetchall()

        categorias = []
        for row in rows:
            categoria = {
                "Id": row[0],
                "Descrição": row[1],
            }
            categorias.append(categoria)

        cursor.close()
        connection.close()
        return categorias

# Motivos
@ns.route('/motivos')
class MotivoResource(Resource):
    @ns.doc('list_motivo')
    @ns.marshal_list_with(motivos_model)
    def get(self):
        motivo = request.args.get('motivo_id')

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            BEGIN
                :ref_cursor := get_motivos(:motivo);
            END;
        """

        ref_cursor = cursor.var(oracledb.CURSOR)

        cursor.execute(query, {
            "ref_cursor": ref_cursor,
            "motivo": motivo,
        })

        result_cursor = ref_cursor.getvalue()

        rows = result_cursor.fetchall()

        motivos = []
        for row in rows:
            motivo = {
                "Id": row[0],
                "Descrição": row[1],
            }
            motivos.append(motivo)

        cursor.close()
        connection.close()
        return motivos

# Cargos
@ns.route('/cargos')
class CargoResource(Resource):
    @ns.doc('list_cargo')
    @ns.marshal_list_with(cargos_model)
    def get(self):
        cargo = request.args.get('cargo_id')

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            BEGIN
                :ref_cursor := get_cargos(:cargo);
            END;
        """

        ref_cursor = cursor.var(oracledb.CURSOR)

        cursor.execute(query, {
            "ref_cursor": ref_cursor,
            "cargo": cargo,
        })

        rows = ref_cursor.getvalue().fetchall()

        cargos = []
        for row in rows:
            cargo = {
                "Id": row[0],
                "Descrição": row[1],
            }
            cargos.append(cargo)

        cursor.close()
        connection.close()
        return cargos

# Departamentos
@ns.route('/departamentos')
class DepartamentoResource(Resource):
    @ns.doc('list_departamento')
    @ns.marshal_list_with(departamentos_model)
    def get(self):
        departamento = request.args.get('departamento_id')

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            BEGIN
                :ref_cursor := get_departamentos(:departamento);
            END;
        """

        ref_cursor = cursor.var(oracledb.CURSOR)

        cursor.execute(query, {
            "ref_cursor": ref_cursor,
            "departamento": departamento,
        })

        rows = ref_cursor.getvalue().fetchall()

        departamentos = []
        for row in rows:
            departamento = {
                "Id": row[0],
                "Descrição": row[1],
            }
            departamentos.append(departamento)

        cursor.close()
        connection.close()
        return departamentos

# Estoque
@ns.route('/estoque')
class EstoqueResource(Resource):
    @ns.doc('list_estoque')
    @ns.marshal_list_with(estoque_model)
    def get(self):
        estoque = request.args.get('estoque_id')
        medicamento = request.args.get('medicamento_id')
        responsavel = request.args.get('responsavel_id')
        tipo_movimentacao = request.args.get('tipo_movimentacao_id')

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            BEGIN
                :ref_cursor := get_estoque(:estoque, :medicamento, :responsavel, :tipo_movimentacao);
            END;
        """

        ref_cursor = cursor.var(oracledb.CURSOR)

        cursor.execute(query, {
            "ref_cursor": ref_cursor,
            "estoque": estoque,
            "medicamento": medicamento,
            "responsavel": responsavel,
            "tipo_movimentacao": tipo_movimentacao,
        })

        rows = ref_cursor.getvalue().fetchall()

        estoque = []
        for row in rows:
            item = {
                "Id": row[0],
                "Medicamento": row[1],
                "Responsável": row[2],
                "Tipo Movimentação": row[3],
                "Quantidade": row[4],
                "Data": row[5],
                "Motivo": row[6],
            }
            estoque.append(item)

        cursor.close()
        connection.close()
        
        return estoque

# Etapas Produção
@ns.route('/etapas_producao')
class EtapasProducaoResource(Resource):
    @ns.doc('list_etapas_producao')
    @ns.marshal_list_with(etapas_producao_model)
    def get(self):
        etapa = request.args.get('etapa_id')

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            BEGIN
                :ref_cursor := get_etapas_producao(:etapa);
            END;
        """

        ref_cursor = cursor.var(oracledb.CURSOR)

        cursor.execute(query, {
            "ref_cursor": ref_cursor,
            "etapa": etapa,
        })

        rows = ref_cursor.getvalue().fetchall()

        etapas_producao = []
        for row in rows:
            etapa = {
                "Id": row[0],
                "Descrição": row[1],
                "Prazo Estimado": row[2],
            }
            etapas_producao.append(etapa)

        cursor.close()
        connection.close()
        return etapas_producao

# Produção
@ns.route('/producao')
class ProducaoResource(Resource):
    @ns.doc('list_producao')
    @ns.marshal_list_with(producao_model)
    def get(self):
        producao = request.args.get('producao_id')
        medicamento = request.args.get('medicamento_id')
        etapa = request.args.get('etapa_id')

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            BEGIN
                :ref_cursor := get_producao(:producao, :medicamento, :etapa);
            END;
        """

        ref_cursor = cursor.var(oracledb.CURSOR)

        cursor.execute(query, {
            "ref_cursor": ref_cursor,
            "producao": producao,
            "medicamento": medicamento,
            "etapa": etapa,
        })

        rows = ref_cursor.getvalue().fetchall()

        producao = []
        for row in rows:
            producao_item = {
                "Id": row[0],
                "Medicamento": row[1],
                "Etapa": row[2],
                "Data Início": row[3],
                "Data Fim Prevista": row[4],
                "Data Fim Real": row[5],
            }
            producao.append(producao_item)

        cursor.close()
        connection.close()
        return producao

# Entradas Previstas
@ns.route('/entradas_previstas')
class EntradasPrevistasResource(Resource):
    @ns.doc('list_entradas_previstas')
    @ns.marshal_list_with(entradas_previstas_model)
    def get(self):
        entrada_prevista = request.args.get('entrada_prevista_id')
        material = request.args.get('material_id')
        medicamento = request.args.get('medicamento_id')

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            BEGIN
                :ref_cursor := get_entradas_previstas(:entrada_prevista, :material, :medicamento);
            END;
        """

        ref_cursor = cursor.var(oracledb.CURSOR)

        cursor.execute(query, {
            "ref_cursor": ref_cursor,
            "entrada_prevista": entrada_prevista,
            "material": material,
            "medicamento": medicamento,
        })

        rows = ref_cursor.getvalue().fetchall()

        entradas_previstas = []
        for row in rows:
            entrada = {
                "Id": row[0],
                "Material": row[1],
                "Medicamento": row[2],
                "Quantidade": row[3],
                "Data Prevista": row[4],
            }
            entradas_previstas.append(entrada)

        cursor.close()
        connection.close()
        return entradas_previstas

# Atrasos Produção
@ns.route('/atrasos_producao')
class AtrasosProducaoResource(Resource):
    @ns.doc('list_atrasos_produção')
    @ns.marshal_list_with(atrasos_producao_model)
    def get(self):
        atraso = request.args.get('atraso_id')
        producao = request.args.get('producao_id')
        medicamento = request.args.get('medicamento_id')
        etapa = request.args.get('etapa_id')

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            BEGIN
                :ref_cursor := get_atrasos_producao(:atraso, :producao, :medicamento, :etapa);
            END;
        """

        ref_cursor = cursor.var(oracledb.CURSOR)

        cursor.execute(query, {
            "ref_cursor": ref_cursor,
            "atraso": atraso,
            "producao": producao,
            "medicamento": medicamento,
            "etapa": etapa,
        })

        rows = ref_cursor.getvalue().fetchall()

        atrasos_producao = []
        for row in rows:
            atraso = {
                "Id": row[0],
                "Medicamento": row[1],
                "Etapa": row[2],
                "Dias de Atraso": row[3],
                "Motivo": row[4],
            }
            atrasos_producao.append(atraso)

        cursor.close()
        connection.close()
        return atrasos_producao
    
# ChatBot
@ns.route('/chatbot')
class ChatBotResource(Resource):
    @ns.doc('chat')
    @ns.expect(chat_message_model)  # Utilize o modelo definido
    def post(self):
        data = request.json
        user_message = data.get("message")

        # Obtenha a resposta do chatbot utilizando o método `get_response`
        bot_response = bot.get_response(user_message)
        
        return {"response": bot_response}

if __name__ == '__main__':
    app.run(debug=True)

# http://localhost:5000/docs
