# Descrição
- Extração dos dados de produção de frutíferas e olerícolas no DF
- Obtenção de 2 arquivos após a extração e limpeza dos dados: frutirefas_formatada.csv e olericolas_formata.csv
- Ambos os arquivos fornecem: alimentos produzidos por cada RA no DF, % total de participação da produção no DF e também total (em toneladas) da produção
- Com isso, utilizamos o script fake_customers_generation.py para gerar 50 compras de 10 clientes diferentes
- A geração de dados funcionou da seguinte forma, para cada cliente:
    - Escolhemos uma RA aleatória
    - Geramos 50 compras
    - Caso o item da compra fosse da mesma RA do cliente, ele compraria algum valor entre 50 e 100
    - Caso não, compraria algum valor entre 1 e 70
- Dessa forma, adicionamos um viés na nossa geração de dados, que podemos verificar com o resultado do treinamento

# Sistema de Recomendação (ai.py)
- Implementação de um sistema de recomendação baseado em similaridade de usuários usando o algoritmo K-Nearest Neighbors (KNN)
- Etapas do processamento:
    1. Carregamento dos dados de vendas do arquivo 'sells_data.csv'
    2. Criação de uma matriz pivot de clientes x produtos, com as quantidades compradas
    3. Conversão para matriz esparsa para otimização de memória
    4. Treinamento do modelo KNN usando:
        - Métrica de similaridade por cosseno (apropriada para dados esparsos)
        - K=5 vizinhos mais próximos
        - Algoritmo de força bruta para busca
    5. Implementação da função de recomendação que:
        - Recebe uma localidade como entrada
        - Encontra os K vizinhos mais similares
        - Soma as compras dos vizinhos
        - Retorna os top 10 produtos mais comprados pelos vizinhos
- Parâmetros configuráveis:
    - K_VIZINHOS = 5 (número de vizinhos similares)
    - K_RECS = 10 (número de recomendações retornadas)

# Resultados da Avaliação
- O sistema foi avaliado utilizando métricas padrão de sistemas de recomendação:
    - Precision@K = 0.372 (37.2%): indica que 37.2% dos itens recomendados eram relevantes
    - Recall@K = 0.472 (47.2%): indica que 47.2% dos itens relevantes foram recuperados nas recomendações
- Estes resultados sugerem que:
    - O sistema tem um bom equilíbrio entre precisão e recall
    - O viés introduzido na geração dos dados (preferência por produtos da mesma RA) foi capturado pelo modelo
    - O algoritmo KNN com similaridade por cosseno foi efetivo em identificar padrões de compra similares
