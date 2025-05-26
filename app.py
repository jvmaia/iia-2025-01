from flask import Flask, jsonify, request, render_template
from ai import recomendar_por_cliente, K_VIZINHOS, K_RECS, localidades, get_client_purchases

app = Flask(__name__)

@app.route('/')
def index():
    client_name = request.args.get('client')
    error = None
    recommendations = None
    purchases = None
    
    if client_name:
        try:
            recommendations = recomendar_por_cliente(
                client=client_name,
                k_vizinhos=K_VIZINHOS,
                k_recs=K_RECS
            )
            purchases = get_client_purchases(client_name)
        except ValueError as e:
            error = str(e)
        except Exception as e:
            error = "Erro interno do servidor"
    
    return render_template('index.html',
                         clients=sorted(localidades),
                         selected_client=client_name,
                         recommendations=recommendations,
                         purchases=purchases,
                         error=error)

@app.route('/api/recommend')
def get_recommendations():
    client_name = request.args.get('client')
    
    if not client_name:
        return jsonify({'error': 'Client name is required'}), 400
    
    try:
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 