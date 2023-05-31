import json

from dbconnect import oracle_connection

caminho_arquivo = 'alimentos.txt'
valores_principais = []
conn = oracle_connection()
cursor = conn.cursor()

def modificar_json(alimento_json):
    alimento_json = json.loads(alimento_json.strip())

    descricao = alimento_json['descricao']

    partes = descricao.split(",")

    principal = partes[0].strip()

    observacoes = [parte.strip().replace("s/", "sem").replace("c/", "com") for parte in partes[1:]]

    observacoes_linha = ", ".join(observacoes)

    observacoes_linha = observacoes_linha.replace(',', '')

    alimento_json['descricao'] = principal if len(observacoes_linha) == 0 else observacoes_linha

    return alimento_json

# INSERINDO OS ALIMENTOS PRINCIPAIS NO BANCO DE DADOS
with open(caminho_arquivo, "r") as file:
    for linha in file:
        alimento_json = modificar_json(linha)

        chave_principal = alimento_json.get('principal')
        if not any(obj.get('principal') == chave_principal for obj in valores_principais):
            valores_principais.append(alimento_json)

for i in valores_principais:
    classe = i['classe']
    alimento = i['principal']

    sql = "INSERT INTO T_GSN_ALIMENTO (CLASSE, ALIMENTO) VALUES (:classe, :alimento)"

    cursor.execute(sql, classe=classe, alimento=alimento)

# INSERINDO AS VARIACOES DOS ALIMENTOS EM OUTRA TABELA
with open(caminho_arquivo, "r") as file:
    for linha in file:
        alimento_json = modificar_json(linha)

        sql = "SELECT ID_ALIMENTO FROM T_GSN_ALIMENTO WHERE ALIMENTO = :principal"
        cursor.execute(sql, principal=alimento_json['principal'])
        row = cursor.fetchone()

        sql = "INSERT INTO T_GSN_VARIACAO_ALIMENTO (ID_ALIMENTO, DESCRICAO) VALUES (:id_alimento, :descricao)"

        cursor.execute(sql, id_alimento=row[0], descricao=alimento_json['descricao'])

conn.commit()

# INSERINDO OS NUTRIENTES DAS VARIACOES DOS ALIMENTOS EM OUTRA TABELA
with open(caminho_arquivo, "r") as file:
    for linha in file:

        alimento_json = modificar_json(linha)

        nutrientes = alimento_json['nutrientes']

        sql = "SELECT ID_VARIACAO_ALIMENTO FROM T_GSN_VARIACAO_ALIMENTO WHERE DESCRICAO = :descricao"
        cursor.execute(sql, descricao=alimento_json['descricao'])
        row = cursor.fetchone()

        for nutriente in nutrientes:
            sql2 = "INSERT INTO T_GSN_NUTRIENTES_ALIMENTO (ID_VARIACAO_ALIMENTO, COMPONENTE, UNIDADE_MEDIDA, VALOR_CEM_G) VALUES (:id_variacao_alimento, :componente, :unidade_medida, :valor_cem_g)"
            cursor.execute(sql2, id_variacao_alimento=row[0], componente=nutriente['Componente'], unidade_medida=nutriente['Unidades'], valor_cem_g=nutriente['Valor por 100g'])

conn.commit()

