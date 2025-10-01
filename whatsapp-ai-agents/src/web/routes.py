from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import json
import logging

# Criar blueprint para as rotas web
web_bp = Blueprint('web', __name__, template_folder='templates', static_folder='static')

# Mock data para agentes (em uma implementação real, isso viria de um banco de dados)
MOCK_AGENTS = [
    {
        "id": "customer_service",
        "name": "Agente de Atendimento",
        "description": "Agente especializado em atendimento ao cliente",
        "status": "active",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 500
    },
    {
        "id": "technical_support",
        "name": "Agente de Suporte Técnico",
        "description": "Agente especializado em suporte técnico",
        "status": "active",
        "model": "gpt-4",
        "temperature": 0.5,
        "max_tokens": 800
    }
]

@web_bp.route('/')
@login_required
def index():
    """Página principal do painel administrativo"""
    return render_template('index.html', agents=MOCK_AGENTS)

@web_bp.route('/agents')
@login_required
def agents():
    """Página de gerenciamento de agentes"""
    return render_template('agents.html', agents=MOCK_AGENTS)

@web_bp.route('/logs')
@login_required
def logs():
    """Página de visualização de logs"""
    return render_template('logs.html')

@web_bp.route('/settings')
@login_required
def settings():
    """Página de configurações"""
    return render_template('settings.html')

# Rotas de API para funcionalidades AJAX

@web_bp.route('/api/logs')
@login_required
def api_logs():
    """API para obter logs em tempo real"""
    # Em uma implementação real, isso viria de um arquivo de log ou banco de dados
    mock_logs = [
        "[INFO] 2023-08-15 10:30:45 - Mensagem recebida de +5511999999999",
        "[INFO] 2023-08-15 10:30:46 - Intenção detectada: customer_service",
        "[INFO] 2023-08-15 10:30:48 - Resposta gerada: Olá! Como posso ajudar?",
        "[INFO] 2023-08-15 10:30:49 - Resposta enviada com sucesso",
        "[INFO] 2023-08-15 10:32:12 - Mensagem recebida de +5511888888888",
        "[INFO] 2023-08-15 10:32:13 - Intenção detectada: technical_support",
        "[INFO] 2023-08-15 10:32:15 - Resposta gerada: Vou ajudar com o problema técnico.",
        "[INFO] 2023-08-15 10:32:16 - Resposta enviada com sucesso"
    ]
    
    return jsonify({"logs": mock_logs})

@web_bp.route('/api/test-agent', methods=['POST'])
@login_required
def api_test_agent():
    """API para testar um agente com uma mensagem de exemplo"""
    data = request.get_json()
    agent_id = data.get('agent_id')
    message = data.get('message')
    
    # Em uma implementação real, isso chamaria o agente real
    mock_responses = {
        "customer_service": "Olá! Agradeço seu contato. Como posso ajudar você hoje?",
        "technical_support": "Entendi que você está enfrentando um problema técnico. Vou ajudar a resolver isso. Primeiro, você poderia reiniciar o dispositivo?"
    }
    
    response = mock_responses.get(agent_id, "Desculpe, não consegui processar sua solicitação.")
    
    return jsonify({"response": response})

@web_bp.route('/api/agent-config', methods=['POST'])
@login_required
def api_agent_config():
    """API para salvar configurações de um agente"""
    data = request.get_json()
    agent_id = data.get('agent_id')
    config = data.get('config')
    
    # Em uma implementação real, isso salvaria no banco de dados
    logging.info(f"Configurações salvas para agente {agent_id}: {config}")
    
    return jsonify({"success": True})

@web_bp.route('/api/stats')
@login_required
def api_stats():
    """API para obter estatísticas de uso"""
    # Em uma implementação real, isso viria de um banco de dados
    stats = {
        "total_conversations": 1243,
        "total_messages": 3456,
        "avg_response_time": "2.3s",
        "satisfaction_rate": "92%"
    }
    
    return jsonify(stats)