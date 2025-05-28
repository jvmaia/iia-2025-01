"""
app.py

Aplicação Flask que fornece:
- Interface web para selecionar clientes e visualizar recomendações e histórico de compras.
- Endpoint RESTful (/api/recommend) para obter recomendações via JSON.
"""

from flask import Flask, jsonify, request, render_template
from ai import recomendar_por_cliente, K_VIZINHOS, K_RECS, localidades, get_client_purchases

# Inicializa a aplicação Flask
enable_debug = True  # Ative em desenvolvimento
app = Flask(__name__)
app.config["DEBUG"] = enable_debug


@app.route("/")
def index():
    """
    Renderiza a página principal com:
    - Dropdown de clientes
    - Recomendações e histórico de compras, se um cliente estiver selecionado
    """
    client_name = request.args.get("client")
    error = None
    recommendations = None
    purchases = None

    if client_name:
        try:
            # Obtém recomendações e histórico de compras para o cliente
            recommendations = recomendar_por_cliente(
                client=client_name, k_vizinhos=K_VIZINHOS, k_recs=K_RECS
            )
            # Obtém o histórico de compras do cliente
            purchases = get_client_purchases(client_name)
        except ValueError as e:
            # Cliente não encontrado
            error = str(e)
        except Exception:
            # Erro genérico no servidor
            error = "Erro interno do servidor"

    # Renderiza template passando lista de clientes e resultados
    return render_template(
        "index.html",
        clients=sorted(localidades),
        selected_client=client_name,
        recommendations=recommendations,
        purchases=purchases,
        error=error,
    )


@app.route("/api/recommend")
def get_recommendations():
    """
    Endpoint API que retorna recomendações via JSON.
    Parâmetros de query:
      - client: nome ou ID do cliente
    Respostas:
      - 200: {'client': ..., 'recommendations': [...]}
      - 400: {'error': 'Client name is required'}
      - 404: {'error': 'Cliente não encontrado'}
      - 500: {'error': 'Internal server error'}
    """
    client_name = request.args.get("client")

    if not client_name:
        # Parâmetro obrigatório não fornecido
        return jsonify({"error": "Client name is required"}), 400

    try:
        # Gera e retorna recomendações em JSON
        recommendations = recomendar_por_cliente(
            client=client_name, k_vizinhos=K_VIZINHOS, k_recs=K_RECS
        )
        return jsonify({"client": client_name, "recommendations": recommendations})
    except ValueError as e:
        # Cliente não encontrado
        return jsonify({"error": str(e)}), 404
    except Exception:
        # Erro inesperado
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Executa o servidor Flask
    app.run(host="0.0.0.0", port=5000)
