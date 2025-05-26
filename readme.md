# Sistema de Recomendação de Produtos

Este é um sistema de recomendação de produtos baseado em similaridade de clientes, utilizando o algoritmo de K-Nearest Neighbors (KNN) com similaridade por cosseno.

## Funcionalidades

- Recomendação de produtos baseada no histórico de compras de clientes similares
- Interface web amigável para seleção de clientes
- Visualização das recomendações de produtos
- Exibição do histórico de compras do cliente selecionado
- API REST para integração com outros sistemas

## Pré-requisitos

- Docker instalado em sua máquina
- Arquivo de dados `sells_data.csv` na pasta `data/` do projeto

## Como Executar

### Usando Docker

1. Clone o repositório e navegue até a pasta do projeto

2. Construa a imagem Docker:
```bash
docker build -t recommendation-api .
```

3. Execute o container:
```bash
docker run -p 5000:5000 -v $(pwd)/data:/app/data recommendation-api
```

Observações:
- A opção `-p 5000:5000` mapeia a porta 5000 do container para a porta 5000 do seu computador
- A opção `-v $(pwd)/data:/app/data` monta a pasta `data` do seu computador dentro do container
- Se a porta 5000 estiver em uso, você pode usar outra porta, por exemplo: `-p 5001:5000`

### Acessando a Interface Web

1. Abra seu navegador e acesse:
```
http://localhost:5000
```
(ou a porta que você escolheu, exemplo: `http://localhost:5001`)

2. Na interface você pode:
   - Selecionar um cliente no menu dropdown
   - Clicar em "Obter Recomendações" para ver as sugestões
   - Ver a lista de produtos recomendados
   - Consultar o histórico de compras do cliente selecionado

### Usando a API

A API também está disponível para integração com outros sistemas:

- Endpoint: `/api/recommend`
- Método: GET
- Parâmetro: `client` (nome do cliente)
- Exemplo de uso:
```bash
curl "http://localhost:5000/api/recommend?client=Lucas"
```

Exemplo de resposta:
```json
{
    "client": "Lucas",
    "recommendations": ["Produto1", "Produto2", "Produto3", ...]
}
```

## Estrutura do Projeto

- `app.py`: Aplicação Flask com rotas web e API
- `ai.py`: Lógica do sistema de recomendação
- `templates/`: Arquivos HTML da interface web
- `data/`: Diretório para armazenar o arquivo de dados
- `Dockerfile`: Configuração para construção da imagem Docker
- `requirements.txt`: Dependências Python do projeto

## Parâmetros do Sistema

- `K_VIZINHOS`: Número de vizinhos similares considerados (padrão: 5)
- `K_RECS`: Número de recomendações retornadas (padrão: 10)

## Tratamento de Erros

A interface web e a API tratam os seguintes casos:
- Cliente não encontrado
- Parâmetros ausentes
- Erros internos do servidor

## Tecnologias Utilizadas

- Python 3.9
- Flask
- Pandas
- Scikit-learn
- Bootstrap 5
- Docker
