from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
import oracledb
import json

app = Flask(__name__)
api = Api(app, version='1.0', title='API StockFlux',
          description='Uma API para gerenciar os dados do dashboard',
          doc='/docs'  # URL para o Swagger UI
          )
CORS(app)

ns = api.namespace('api', description='Operações relacionadas às tabelas')

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

# Função para carregar credenciais a partir de um arquivo JSON
def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)

# Função para obter a conexão com o banco de dados
def get_db_connection():
    credentials = load_credentials()
    connection = oracledb.connect(user=credentials['user'], password=credentials['password'], dsn=credentials['dsn'])
    return connection

# Medicamentos
@ns.route('/medicamentos')
class MedicamentoResource(Resource):
    @ns.doc('list_medicamentos')
    @ns.marshal_list_with(medicamento_model)
    def get(self):
        categoria_id = request.args.get('categoria_id')
        motivo_id = request.args.get('motivo_id')
        status_id = request.args.get('status_id')
        medicamento_nome = request.args.get('medicamento_nome')

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
            "categoria": categoria_id,
            "motivo": motivo_id,
            "status": status_id,
            "medicamento": medicamento_nome
        })

        # Obter os resultados do cursor retornado
        rows = ref_cursor.getvalue().fetchall()

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

        cursor.close()
        connection.close()
        return medicamentos

# Status
@ns.route('/status')
class StatusResource(Resource):
    @ns.doc('list_status')
    @ns.marshal_list_with(status_model)
    def get(self):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id_status, descricao, motivo FROM rm93069.status")
        rows = cursor.fetchall()

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
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id_fornecedor, nome, telefone, email FROM rm93069.fornecedores")
        rows = cursor.fetchall()

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
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id_material, f.nome, descricao FROM rm93069.materiais m join rm93069.fornecedores f on m.id_fornecedor = f.id_fornecedor")
        rows = cursor.fetchall()

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
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id_categoria, descricao FROM rm93069.categorias")
        rows = cursor.fetchall()

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
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id_motivo, descricao FROM rm93069.motivos")
        rows = cursor.fetchall()

        motivos = []
        for row in rows:
            motivo = {
                "ID Motivo": row[0],
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
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id_cargo, descricao FROM rm93069.cargos")
        rows = cursor.fetchall()

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
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id_departamento, descricao FROM rm93069.departamentos")
        rows = cursor.fetchall()

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
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id_estoque, m.nome, r.nome, tm.descricao, quantidade, data, motivo "
            "FROM rm93069.estoque e "
            "join rm93069.tipo_movimentacoes tm on e.id_tipo_movimentacao = tm.id_tipo_movimentacao "
            "join rm93069.responsaveis r on e.id_responsavel = r.id_responsavel "
            "join rm93069.medicamentos m on e.id_medicamento = m.id_medicamento")
        rows = cursor.fetchall()

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
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id_etapa, descricao, prazo_estimado FROM rm93069.etapas_producao")
        rows = cursor.fetchall()

        etapas_producao = []
        for row in rows:
            etapa = {
                "ID Etapa": row[0],
                "Descrição": row[1],
                "Prazo Estimado (dias)": row[2],
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
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id_producao, m.nome, ep.descricao, data_inicio, data_fim_prevista, data_fim_real "
            "FROM rm93069.producao p "
            "join rm93069.medicamentos m on p.id_medicamento = m.id_medicamento "
            "join rm93069.etapas_producao ep on p.id_etapa = ep.id_etapa")
        rows = cursor.fetchall()

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
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id_entrada_prevista, ma.descricao, m.nome, quantidade, data_prevista "
            "FROM rm93069.entradas_previstas ep "
            "join rm93069.medicamentos m on ep.id_medicamento = m.id_medicamento "
            "join rm93069.materiais ma on ep.id_material = ma.id_material")
        rows = cursor.fetchall()

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
@ns.route('/atrasos_produção')
class AtrasosProducaoResource(Resource):
    @ns.doc('list_atrasos_produção')
    @ns.marshal_list_with(atrasos_producao_model)
    def get(self):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id_atraso, m.nome, ep.descricao, dias_atraso, motivo "
                       "FROM rm93069.atrasos_producao ap "
                       "join rm93069.producao p on p.id_producao = ap.id_producao "
                       "join rm93069.medicamentos m on p.id_medicamento = m.id_medicamento "
                       "join rm93069.etapas_producao ep on p.id_etapa = ep.id_etapa")
        rows = cursor.fetchall()

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

# Ponto de entrada da aplicação
if __name__ == '__main__':
    app.run(debug=True)

# http://localhost:5000/docs
