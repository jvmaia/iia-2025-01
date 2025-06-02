
# 🚀 Sistema de Recomendação de Produtos

Este é um sistema de recomendação de produtos baseado na similaridade entre clientes, utilizando o algoritmo de **K-Nearest Neighbors (KNN)** com **similaridade por cosseno**. Acesse uma [DEMO](https://teusdv.link/IIA/)!

---

## ✨ Funcionalidades

✅ Recomendação de produtos com base no histórico de compras de clientes similares  
✅ Interface web intuitiva para seleção de clientes  
✅ Visualização clara das recomendações de produtos  
✅ Exibição do histórico de compras do cliente selecionado  
✅ API REST para integração com outros sistemas  

---

## 🛠️ Pré-requisitos

- ✅ Docker instalado em sua máquina
- ✅ Arquivo de dados `sells_data.csv` na pasta `data/` do projeto

---

## 🚀 Como Executar

### 🐳 Usando Docker

1️⃣ Clone o repositório e navegue até a pasta do projeto:

```bash
git clone https://github.com/jvmaia/iia-2025-01.git
cd iia-2025-01
```

2️⃣ Construa a imagem Docker:

```bash
docker build -t recommendation-api .
```

3️⃣ Execute o container:

```bash
docker run -p 5000:5000 -v $(pwd)/data:/app/data recommendation-api
```

⚠️ Observações:
- `-p 5000:5000` → mapeia a porta 5000 do container para a porta 5000 do seu computador
- `-v $(pwd)/data:/app/data` → monta a pasta `data` local dentro do container
- Caso a porta 5000 esteja ocupada, altere para outra porta, por exemplo: `-p 5001:5000`

---

### 🌐 Acessando a Interface Web

1️⃣ Abra seu navegador e acesse:

```
http://localhost:5000
```

(ou `http://localhost:5001` se tiver alterado a porta)

2️⃣ Utilize a interface para:

- 🔽 Selecionar um cliente
- 🖱️ Clicar em "Obter Recomendações"
- 📃 Visualizar produtos recomendados
- 🕘 Consultar histórico de compras do cliente

---

### 🔗 Usando a API

✅ A API está disponível para integração com outros sistemas:

- **Endpoint**: `/api/recommend`
- **Método**: GET
- **Parâmetro**: `client` (nome do cliente)

Exemplo de requisição:

```bash
curl "http://localhost:5000/api/recommend?client=Lucas"
```

Exemplo de resposta:

```json
{
    "client": "Lucas",
    "recommendations": ["Produto1", "Produto2", "Produto3"]
}
```

---

## 📂 Estrutura do Projeto

- `app.py` → Aplicação Flask com rotas web e API
- `ai.py` → Lógica do sistema de recomendação
- `templates/` → Arquivos HTML da interface web
- `data/` → Diretório para armazenar os dados
- `Dockerfile` → Configuração para construção da imagem Docker
- `requirements.txt` → Dependências Python do projeto

---

## 🛡️ Tratamento de Erros

✅ Cliente não encontrado  
✅ Parâmetros ausentes  
✅ Erros internos do servidor  

---

## 📸 Prints

**Recomendação:**

<img width="600" alt="Recomendação" src="https://github.com/user-attachments/assets/ab7a38a1-e64f-4581-ba90-4aaa57c62bc8" />

**Histórico de compras:**

<img width="600" alt="Histórico" src="https://github.com/user-attachments/assets/fab409b7-01dc-4f26-b51c-c166609e9be5" />

---

## 🧰 Tecnologias Utilizadas

- 🐍 Python3
- 🌐 Flask
- 📊 Pandas
- 🤖 Scikit-learn
- 🧵 Multi-threading
- 🎨 Bootstrap 5
- 🐳 Docker

---

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir _issues_ ou enviar _pull requests_.

---

## 📄 Licença

Liberado sob uma licença de uso geral no contexto da UnB.

Consulte `LICENSE` para obter mais detalhes.