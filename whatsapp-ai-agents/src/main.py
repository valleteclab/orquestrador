import os
import sys
import logging
from flask import Flask, request, jsonify
from flask_login import LoginManager
import redis
from src.config.config import Config
from src.orchestrator.orchestrator import AgentOrchestrator
from src.orchestrator.specialized_agents import TechnicalSupportAgent, FinancialAgent
from src.agents.customer_service_agent import CustomerServiceAgent
from src.web.routes import web_bp
import json
from datetime import datetime

# Criar diretório de logs se não existir
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """Cria e configura a aplicação Flask"""
    app = Flask(__name__)
    app.secret_key = Config.API_SECRET_KEY
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'web.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from src.web.routes import User
        return User(user_id)
    
    # Registrar blueprints
    app.register_blueprint(web_bp, url_prefix='/admin')
    
    return app

# Validar configuração antes de iniciar
try:
    Config.validate()
    logger.info("Configuração validada com sucesso")
except ValueError as e:
    logger.error(f"Erro na configuração: {e}")
    sys.exit(1)

# Criar aplicação Flask
app = create_app()

class ChatwootClient:
    """Cliente para interagir com a API do Chatwoot"""
    def __init__(self, api_key, account_id, base_url):
        self.api_key = api_key
        self.account_id = account_id
        self.base_url = base_url.rstrip('/') if base_url else ''
        self.headers = {
            'api_access_token': self.api_key,
            'Content-Type': 'application/json'
        }
        
    def send_message(self, conversation_id, message):
        """Envia uma mensagem para uma conversa no Chatwoot"""
        import requests
        url = f"{self.base_url}/api/v1/accounts/{self.account_id}/conversations/{conversation_id}/messages"
        payload = {
            'content': message,
            'message_type': 'outgoing'
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar mensagem para Chatwoot: {e}")
            return None

class ChatwootBot:
    """Bot principal que integra agentes de IA com Chatwoot"""
    def __init__(self, config):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True
        )
        
        # Inicializar cliente Chatwoot
        self.chatwoot_client = ChatwootClient(
            api_key=config.CHATWOOT_API_KEY,
            account_id=config.CHATWOOT_ACCOUNT_ID,
            base_url=config.CHATWOOT_BASE_URL
        )
        
        # Inicializar orquestrador de agentes
        self.orchestrator = AgentOrchestrator()
        
        # Registrar agentes especializados
        self.orchestrator.register_agent('customer_service', CustomerServiceAgent('customer_service'))
        self.orchestrator.register_agent('technical_support', TechnicalSupportAgent('technical_support'))
        self.orchestrator.register_agent('financial', FinancialAgent('financial'))
        
        logger.info("ChatwootBot inicializado com sucesso")
        
    def process_incoming_message(self, data):
        """Processa mensagens recebidas do Chatwoot"""
        try:
            # Extrair informações da mensagem
            message_content = data.get('message', {}).get('content', '')
            conversation_id = data.get('conversation', {}).get('id')
            contact_id = data.get('contact', {}).get('id')
            contact_name = data.get('contact', {}).get('name', 'Usuário')
            
            if not message_content or not conversation_id:
                logger.warning("Mensagem recebida sem conteúdo ou ID de conversa")
                return
                
            logger.info(f"Mensagem recebida de {contact_name} ({contact_id}): {message_content}")
            
            # Selecionar agente apropriado com base no conteúdo
            agent_id = self.orchestrator.select_agent(message_content)
            logger.info(f"Agente selecionado: {agent_id}")
            
            # Obter resposta do agente
            response = self.orchestrator.get_agent_response(agent_id, message_content, contact_id)
            
            if response:
                # Enviar resposta de volta via Chatwoot
                self.chatwoot_client.send_message(conversation_id, response)
                logger.info(f"Resposta enviada para {contact_name}: {response}")
            else:
                logger.error("Nenhuma resposta gerada pelo agente")
                
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            # Enviar mensagem de erro genérica
            # self.chatwoot_client.send_message(conversation_id, "Desculpe, ocorreu um erro ao processar sua mensagem.")

# Inicializar bot
try:
    chatwoot_bot = ChatwootBot(Config)
except Exception as e:
    logger.error(f"Erro ao inicializar ChatwootBot: {e}")
    chatwoot_bot = None

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint para receber webhooks do Chatwoot"""
    if not chatwoot_bot:
        logger.error("ChatwootBot não foi inicializado corretamente")
        return jsonify({'error': 'Serviço indisponível'}), 503
        
    data = request.get_json()
    
    # Verificar se é uma mensagem de entrada
    if data.get('message_type') == 'incoming':
        # Processar em background para não bloquear o webhook
        import threading
        thread = threading.Thread(target=chatwoot_bot.process_incoming_message, args=(data,))
        thread.start()
    
    return jsonify({'status': 'received'})

@app.route('/api/test-agent', methods=['POST'])
def test_agent():
    """Endpoint para testar agentes de IA"""
    if not chatwoot_bot:
        return jsonify({'error': 'Serviço indisponível'}), 503
        
    data = request.get_json()
    agent_id = data.get('agent_id')
    message = data.get('message')
    
    if not agent_id or not message:
        return jsonify({'error': 'agent_id e message são obrigatórios'}), 400
    
    try:
        response = chatwoot_bot.orchestrator.get_agent_response(agent_id, message, 'test_user')
        return jsonify({'response': response})
    except Exception as e:
        logger.error(f"Erro ao testar agente: {e}")
        return jsonify({'error': 'Erro ao processar mensagem'}), 500

@app.route('/api/logs')
def get_logs():
    """Endpoint para obter logs em tempo real"""
    try:
        with open('logs/app.log', 'r') as f:
            lines = f.readlines()
            # Obter as últimas 50 linhas
            latest_logs = lines[-50:] if len(lines) > 50 else lines
            return jsonify({'logs': [line.strip() for line in latest_logs]})
    except FileNotFoundError:
        return jsonify({'logs': []})

@app.route('/api/stats')
def get_stats():
    """Endpoint para obter estatísticas"""
    # Em uma implementação real, isso viria de métricas coletadas
    stats = {
        'total_conversations': 124,
        'total_messages': 542,
        'avg_response_time': '1.2s',
        'satisfaction_rate': '94%'
    }
    return jsonify(stats)

if __name__ == '__main__':
    # Executar aplicação Flask
    app.run(host='0.0.0.0', port=5000, debug=True)