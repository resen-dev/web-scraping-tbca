import json
import requests
from bs4 import BeautifulSoup

caminho_arquivo = "alimentos.txt"
valores_principais = []

url_base = 'http://www.tbca.net.br/base-dados/composicao_alimentos.php'

cod_alimentos = []

parametros = {'pagina': 1}

continuar_loop = True

while continuar_loop:
    response = requests.get(url_base, params=parametros)

    if response.status_code == 200:
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')

        tbody_element = soup.find('tbody')

        if tbody_element:

            tr_elements = tbody_element.find_all('tr')

            if tr_elements:

                for tr in tr_elements:
                    td_1 = tr.find_all('td')[0].text.strip()
                    td_5 = tr.find_all('td')[4].text.strip()
                    cod_alimentos.append((td_1, td_5))
            else:

                continuar_loop = False
        else:

            continuar_loop = False

        parametros['pagina'] += 1

    else:
        continuar_loop = False

cod_alimentos = list(set(cod_alimentos))

result = []

for cod_alimento, classe_alimento in cod_alimentos:

    url = f'http://www.tbca.net.br/base-dados/int_composicao_alimentos.php?cod_produto={cod_alimento}'

    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')

    description_element = soup.find('h5', {'id': 'overview'})
    descricao = description_element.text.split('Descrição:')[1].split('<<')[0].strip()

    table = soup.find('table')

    thead = table.find('thead')
    headers = thead.find_all('th')[:3]

    tbody = table.find('tbody')
    rows = tbody.find_all('tr')

    nutrientes = []

    for row in rows:
        values = row.find_all('td')[:3]
        row_data = {}
        for i, header in enumerate(headers):
            row_data[header.text.strip()] = values[i].text.strip()
        nutrientes.append(row_data)

    alimento_json = {
        'codigo': cod_alimento,
        'classe': classe_alimento,
        'descricao': descricao,
        'nutrientes': nutrientes
    }

    with open(caminho_arquivo, "a") as file:

        produto_json_str = json.dumps(alimento_json)

        file.write(produto_json_str + "\n")

