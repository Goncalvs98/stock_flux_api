from flask import Flask, jsonify
from flask_cors import CORS  # Adicione esta linha
import oracledb
import json

app = Flask(__name__)
CORS(app)  # Adicione esta linha para permitir CORS
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
@app.route('/get_medicamentos', methods=['GET'])
def get_medicamentos():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT c.descricao AS Categoria, mt.descricao AS Motivo, nome, codigo, quantidade_minima, localizacao, s.descricao AS Status "
                   "FROM rm93069.medicamentos m "
                   "JOIN rm93069.categorias c ON m.id_categoria = c.id_categoria "
                   "JOIN rm93069.motivos mt ON m.id_motivo = mt.id_motivo "
                   "JOIN rm93069.status_medicamento sm ON m.id_medicamento = sm.id_medicamento "
                   "JOIN rm93069.status s ON sm.id_status = s.id_status")
    rows = cursor.fetchall()

    cargos = []
    for row in rows:
        cargo = {
            "Categoria": row[0],
            "Motivo": row[1],
            "Nome": row[2],
            "Código": row[3],
            "Quantidade Minima": row[4],
            "Localização": row[5],
            "Status": row[6],
        }
        cargos.append(cargo)

    cursor.close()
    connection.close()
    return jsonify(cargos)

# Status
@app.route('/get_status', methods=['GET'])
def get_status():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id_status, descricao, motivo FROM rm93069.status")
    rows = cursor.fetchall()

    status_list = []
    for row in rows:
        status_item = {
            "ID Status": row[0],
            "Descrição": row[1],
            "Motivo": row[2],
        }
        status_list.append(status_item)

    cursor.close()
    connection.close()
    return jsonify(status_list)

# Fornecedores
@app.route('/get_fornecedores', methods=['GET'])
def get_fornecedores():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id_fornecedor, nome, telefone, email FROM rm93069.fornecedores")
    rows = cursor.fetchall()

    fornecedores = []
    for row in rows:
        fornecedor = {
            "ID Fornecedor": row[0],
            "Nome": row[1],
            "Telefone": row[2],
            "Email": row[3],
        }
        fornecedores.append(fornecedor)

    cursor.close()
    connection.close()
    return jsonify(fornecedores)

# Histórico Fornecedores
@app.route('/get_historico_fornecedor', methods=['GET'])
def get_historico_fornecedor():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id_historico, id_fornecedor, historico FROM rm93069.historico_fornecedor")
    rows = cursor.fetchall()

    historicos = []
    for row in rows:
        historico = {
            "ID Histórico": row[0],
            "ID Fornecedor": row[1],
            "Histórico": row[2],
        }
        historicos.append(historico)

    cursor.close()
    connection.close()
    return jsonify(historicos)

# Materiais
@app.route('/get_materiais', methods=['GET'])
def get_materiais():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id_material, id_fornecedor, descricao FROM rm93069.materiais")
    rows = cursor.fetchall()

    materiais = []
    for row in rows:
        material = {
            "ID Material": row[0],
            "ID Fornecedor": row[1],
            "Descrição": row[2],
        }
        materiais.append(material)

    cursor.close()
    connection.close()
    return jsonify(materiais)

# Categorias
@app.route('/get_categorias', methods=['GET'])
def get_categorias():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id_categoria, descricao FROM rm93069.categorias")
    rows = cursor.fetchall()

    categorias = []
    for row in rows:
        categoria = {
            "ID Categoria": row[0],
            "Descrição": row[1],
        }
        categorias.append(categoria)

    cursor.close()
    connection.close()
    return jsonify(categorias)

# Motivos
@app.route('/get_motivos', methods=['GET'])
def get_motivos():
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
    return jsonify(motivos)

@app.route('/get_materiais_medicamentos', methods=['GET'])
def get_materiais_medicamentos():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id_material, id_medicamento FROM rm93069.materiais_medicamentos")
    rows = cursor.fetchall()

    materiais_medicamentos = []
    for row in rows:
        item = {
            "ID Material": row[0],
            "ID Medicamento": row[1],
        }
        materiais_medicamentos.append(item)

    cursor.close()
    connection.close()
    return jsonify(materiais_medicamentos)

# Cargos
@app.route('/get_cargos', methods=['GET'])
def get_cargos():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id_cargo, descricao FROM rm93069.cargos")
    rows = cursor.fetchall()

    cargos = []
    for row in rows:
        cargo = {
            "ID Cargo": row[0],
            "Descrição": row[1],
        }
        cargos.append(cargo)

    cursor.close()
    connection.close()
    return jsonify(cargos)

# Departamentos
@app.route('/get_departamentos', methods=['GET'])
def get_departamentos():
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
    return jsonify(departamentos)

# Responsáveis
@app.route('/get_responsaveis', methods=['GET'])
def get_responsaveis():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id_responsavel, id_departamento, id_cargo, nome FROM rm93069.responsaveis")
    rows = cursor.fetchall()

    responsaveis = []
    for row in rows:
        responsavel = {
            "ID Responsável": row[0],
            "ID Departamento": row[1],
            "ID Cargo": row[2],
            "Nome": row[3],
        }
        responsaveis.append(responsavel)

    cursor.close()
    connection.close()
    return jsonify(responsaveis)

# Tipo de Movimentações
@app.route('/get_tipo_movimentacoes', methods=['GET'])
def get_tipo_movimentacoes():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id_tipo_movimentacao, descricao FROM rm93069.tipo_movimentacoes")
    rows = cursor.fetchall()

    tipo_movimentacoes = []
    for row in rows:
        tipo_movimentacao = {
            "ID Tipo Movimentação": row[0],
            "Descrição": row[1],
        }
        tipo_movimentacoes.append(tipo_movimentacao)

    cursor.close()
    connection.close()
    return jsonify(tipo_movimentacoes)

# Estoque
@app.route('/get_estoque', methods=['GET'])
def get_estoque():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id_estoque, id_medicamento, id_responsavel, id_tipo_movimentacao, quantidade, data, motivo FROM rm93069.estoque")
    rows = cursor.fetchall()

    estoque = []
    for row in rows:
        item = {
            "ID Estoque": row[0],
            "ID Medicamento": row[1],
            "ID Responsável": row[2],
            "ID Tipo Movimentação": row[3],
            "Quantidade": row[4],
            "Data": row[5],
            "Motivo": row[6],
        }
        estoque.append(item)

    cursor.close()
    connection.close()
    return jsonify(estoque)

# Etapas Produção
@app.route('/get_etapas_producao', methods=['GET'])
def get_etapas_producao():
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
    return jsonify(etapas_producao)

# Produção
@app.route('/get_producao', methods=['GET'])
def get_producao():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id_producao, id_medicamento, id_etapa, data_inicio, data_fim_prevista, data_fim_real FROM rm93069.producao")
    rows = cursor.fetchall()

    producao = []
    for row in rows:
        producao_item = {
            "ID Produção": row[0],
            "ID Medicamento": row[1],
            "ID Etapa": row[2],
            "Data Início": row[3],
            "Data Fim Prevista": row[4],
            "Data Fim Real": row[5],
        }
        producao.append(producao_item)

    cursor.close()
    connection.close()
    return jsonify(producao)

# Status Medicamentos
@app.route('/get_status_medicamento', methods=['GET'])
def get_status_medicamento():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id_status_medicamento, id_medicamento, id_status, data FROM rm93069.status_medicamento")
    rows = cursor.fetchall()

    status_medicamento = []
    for row in rows:
        status_item = {
            "ID Status Medicamento": row[0],
            "ID Medicamento": row[1],
            "ID Status": row[2],
            "Data": row[3],
        }
        status_medicamento.append(status_item)

    cursor.close()
    connection.close()
    return jsonify(status_medicamento)

# Entradas Previstas
@app.route('/get_entradas_previstas', methods=['GET'])
def get_entradas_previstas():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id_entrada_prevista, id_material, id_medicamento, quantidade, data_prevista FROM rm93069.entradas_previstas")
    rows = cursor.fetchall()

    entradas_previstas = []
    for row in rows:
        entrada = {
            "ID Entrada Prevista": row[0],
            "ID Material": row[1],
            "ID Medicamento": row[2],
            "Quantidade": row[3],
            "Data Prevista": row[4],
        }
        entradas_previstas.append(entrada)

    cursor.close()
    connection.close()
    return jsonify(entradas_previstas)

# Atrasos Produção
@app.route('/get_atrasos_producao', methods=['GET'])
def get_atrasos_producao():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id_atraso, id_producao, id_etapa, dias_atraso, motivo FROM rm93069.atrasos_producao")
    rows = cursor.fetchall()

    atrasos_producao = []
    for row in rows:
        atraso = {
            "ID Atraso": row[0],
            "ID Produção": row[1],
            "ID Etapa": row[2],
            "Dias de Atraso": row[3],
            "Motivo": row[4],
        }
        atrasos_producao.append(atraso)

    cursor.close()
    connection.close()
    return jsonify(atrasos_producao)

# Ponto de entrada da aplicação
if __name__ == '__main__':
    app.run(debug=True)
