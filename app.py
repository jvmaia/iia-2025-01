"""
Aplicação web Flask para o sistema de recomendação de produtos agrícolas.
Fornece uma interface web e uma API REST para acessar as recomendações.
"""

from flask import Flask, jsonify, request, render_template
from ai import recomendar_por_cliente, K_VIZINHOS, K_RECS, localidades, get_client_purchases

# Inicialização da aplicação Flask
app = Flask(__name__)

@app.route('/')
def index():
    """
    Rota principal da aplicação web.
    Renderiza a página inicial com o formulário de recomendação e exibe os resultados.
    
    Query Parameters:
        client (str): Nome do cliente para gerar recomendações
    
    Returns:
        str: Página HTML renderizada com os resultados
    """
    client_name = request.args.get('client')
    error = None
    recommendations = None
    purchases = None
    
    if client_name:
        try:
            # Gera recomendações para o cliente selecionado
            recommendations = recomendar_por_cliente(
                client=client_name,
                k_vizinhos=K_VIZINHOS,
                k_recs=K_RECS
            )
            # Obtém o histórico de compras do cliente
            purchases = get_client_purchases(client_name)
        except ValueError as e:
            error = str(e)
        except Exception as e:
            error = "Erro interno do servidor"
    
    # Renderiza o template com os dados
    return render_template('index.html',
                         clients=sorted(localidades),
                         selected_client=client_name,
                         recommendations=recommendations,
                         purchases=purchases,
                         error=error)

@app.route('/api/recommend')
def get_recommendations():
    """
    Endpoint da API REST para obter recomendações.
    
    Query Parameters:
        client (str): Nome do cliente para gerar recomendações
    
    Returns:
        JSON: Objeto contendo as recomendações ou mensagem de erro
        
    HTTP Status Codes:
        200: Sucesso
        400: Parâmetro client não fornecido
        404: Cliente não encontrado
        500: Erro interno do servidor
    """
    client_name = request.args.get('client')
    
    if not client_name:
        return jsonify({'error': 'Client name is required'}), 400
    
    try:
        # Gera recomendações para o cliente
        recommendations = recomendar_por_cliente(
            client=client_name,
            k_vizinhos=K_VIZINHOS,
            k_recs=K_RECS
        )
        return jsonify({
            'client': client_name,
            'recommendations': recommendations
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

# Inicia o servidor Flask em modo debug quando executado diretamente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 