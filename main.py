from flask import Flask, jsonify
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
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT c.descricao AS Categoria, mt.descricao AS Motivo, nome, codigo, quantidade_minima, localizacao, s.descricao AS Status "
                       "FROM rm93069.medicamentos m "
                       "JOIN rm93069.categorias c ON m.id_categoria = c.id_categoria "
                       "JOIN rm93069.motivos mt ON m.id_motivo = mt.id_motivo "
                       "JOIN rm93069.status_medicamento sm ON m.id_medicamento = sm.id_medicamento "
                       "JOIN rm93069.status s ON sm.id_status = s.id_status")
        rows = cursor.fetchall()

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
                "ID Departamento": row[0],
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

# Ponto de entrada da aplicação
if __name__ == '__main__':
    app.run(debug=True)

# http://localhost:5000/docs
