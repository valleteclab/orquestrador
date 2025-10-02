from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from flask_login import login_required, login_user, UserMixin, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import logging
from src.orchestrator.orchestrator import AgentOrchestrator
from src.orchestrator.specialized_agents import TechnicalSupportAgent, FinancialAgent
from src.agents.customer_service_agent import CustomerServiceAgent
import os

# Criar blueprint para as rotas web
web_bp = Blueprint('web', __name__, template_folder='templates', static_folder='static')

# Modelo de usuário para autenticação
class User(UserMixin):
    def __init__(self, id):
        self.id = id

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

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificar credenciais (em produção, use um sistema de autenticação seguro)
        if username == os.getenv('ADMIN_USERNAME', 'admin') and \
           password == os.getenv('ADMIN_PASSWORD', 'admin123'):
            user = User(username)
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('web.index'))
        else:
            return "Credenciais inválidas", 401
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login - WhatsApp AI Agents</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card mt-5">
                        <div class="card-header">
                            <h3 class="card-title">Login - WhatsApp AI Agents</h3>
                        </div>
                        <div class="card-body">
                            <form method="post">
                                <div class="form-group">
                                    <label for="username">Usuário</label>
                                    <input type="text" class="form-control" id="username" name="username" required>
                                </div>
                                <div class="form-group">
                                    <label for="password">Senha</label>
                                    <input type="password" class="form-control" id="password" name="password" required>
                                </div>
                                <button type="submit" class="btn btn-primary">Entrar</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@web_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('web.login'))

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

@web_bp.route('/create-agent', methods=['GET', 'POST'])
@login_required
def create_agent():
    """Página para criar novo agente"""
    if request.method == 'POST':
        # Lógica para criar novo agente
        data = request.get_json()
        agent_id = data.get('agent_id')
        agent_name = data.get('agent_name')
        agent_type = data.get('agent_type')
        model = data.get('model', 'gpt-3.5-turbo')
        temperature = float(data.get('temperature', 0.7))
        max_tokens = int(data.get('max_tokens', 500))
        description = data.get('description', '')
        
        # Em uma implementação real, isso salvaria no banco de dados
        new_agent = {
            "id": agent_id,
            "name": agent_name,
            "description": description,
            "status": "active",
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "type": agent_type
        }
        
        MOCK_AGENTS.append(new_agent)
        logging.info(f"Novo agente criado: {agent_id}")
        
        return jsonify({"success": True, "agent": new_agent})
    
    return render_template('create_agent.html')

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