from flask import Flask, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from src.config.config import Config
from src.utils.session_manager import SessionManager, ChatwootClient
from src.agents.customer_service_agent import CustomerServiceAgent, TechnicalSupportAgent
from src.web.routes import web_bp
import logging
import traceback
import json
import requests
from functools import wraps
import os

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização da aplicação Flask
app = Flask(__name__)

# Carregar configurações
config = Config()
config.load_from_env()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'sua_chave_secreta_aqui')

# Inicialização do LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'web.login'

# Modelo de usuário para autenticação
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificar credenciais (em produção, use um sistema de autenticação seguro)
        if username == os.getenv('ADMIN_USERNAME', 'admin') and \
           password == os.getenv('ADMIN_PASSWORD', 'admin123'):
            user = User(username)
            login_user(user)
            return redirect(url_for('web.index'))
        else:
            return "Credenciais inválidas", 401
    
    return '''
    <form method="post">
        Usuário: <input type="text" name="username"><br>
        Senha: <input type="password" name="password"><br>
        <input type="submit" value="Login">
    </form>
    '''

# Rota de logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Classe para integração com Chatwoot
class ChatwootBot:
    def __init__(self, config):
        self.config = config
        self.session_manager = SessionManager(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB
        )
        self.chatwoot_client = ChatwootClient(
            base_url=config.CHATWOOT_URL,
            api_token=config.CHATWOOT_API_TOKEN
        )
        
        # Inicializar agentes
        self.customer_service_agent = CustomerServiceAgent()
        self.customer_service_agent.initialize_openai(config.OPENAI_API_KEY)
        
        self.technical_support_agent = TechnicalSupportAgent()
        self.technical_support_agent.initialize_openai(config.OPENAI_API_KEY)
        
    def _detect_intent(self, message: str) -> str:
        """Detecta a intenção da mensagem para rotear ao agente apropriado"""
        message_lower = message.lower()
        
        # Palavras-chave para suporte técnico
        technical_keywords = [
            'problema', 'não funciona', 'erro', 'falha', 'quebrado',
            'instalar', 'configurar', 'conectar', 'acessar', 'login',
            'senha', 'conta', 'cadastro', 'sistema', 'aplicativo'
        ]
        
        # Verificar se há palavras-chave técnicas
        for keyword in technical_keywords:
            if keyword in message_lower:
                return 'technical_support'
        
        # Por padrão, encaminhar para atendimento ao cliente
        return 'customer_service'
    
    def _get_agent(self, intent: str):
        """Retorna o agente apropriado com base na intenção"""
        if intent == 'technical_support':
            return self.technical_support_agent
        else:
            return self.customer_service_agent
    
    def process_message(self, data: dict):
        """Processa uma mensagem recebida do Chatwoot"""
        try:
            # Extrair informações da mensagem
            message_data = data.get('message', {})
            message_content = message_data.get('content', '')
            sender = message_data.get('sender', {})
            contact_identifier = sender.get('identifier', '')
            
            if not message_content or not contact_identifier:
                logger.warning("Mensagem inválida recebida")
                return
            
            logger.info(f"Mensagem recebida de {contact_identifier}: {message_content}")
            
            # Recuperar ou criar sessão
            session = self.session_manager.get_session(contact_identifier)
            if not session:
                self.session_manager.create_session(contact_identifier)
                session = self.session_manager.get_session(contact_identifier)
            
            # Detectar intenção e selecionar agente
            intent = self._detect_intent(message_content)
            agent = self._get_agent(intent)
            
            # Processar mensagem com o agente
            response = agent.process_message(message_content, session)
            
            # Enviar resposta através do Chatwoot
            self.send_response(contact_identifier, response)
            
            # Atualizar sessão
            self.session_manager.update_session(contact_identifier, session)
            
            logger.info(f"Resposta enviada para {contact_identifier}: {response}")
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            traceback.print_exc()
    
    def send_response(self, contact_identifier: str, message: str):
        """Envia uma resposta através do Chatwoot"""
        try:
            inbox_id = int(self.config.CHATWOOT_INBOX_ID)
            self.chatwoot_client.send_message(inbox_id, contact_identifier, message)
        except Exception as e:
            logger.error(f"Erro ao enviar resposta para {contact_identifier}: {e}")

# Inicializar o bot do Chatwoot
chatwoot_bot = ChatwootBot(config)

# Rota para webhook do Chatwoot
@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint para receber webhooks do Chatwoot"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados inválidos"}), 400
        
        # Processar mensagem
        chatwoot_bot.process_message(data)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        traceback.print_exc()
        return jsonify({"error": "Erro interno"}), 500

# Rota para autenticação de API
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """Endpoint para autenticação via API"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Token não fornecido"}), 401
        
        token = auth_header.split(' ')[1]
        expected_token = os.getenv('API_KEY')
        
        if not expected_token or token != expected_token:
            return jsonify({"error": "Token inválido"}), 401
        
        return jsonify({"status": "authenticated"}), 200
    except Exception as e:
        logger.error(f"Erro na autenticação: {e}")
        return jsonify({"error": "Erro interno"}), 500

# Decorator para verificar chave de API
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Token não fornecido"}), 401
        
        token = auth_header.split(' ')[1]
        expected_token = os.getenv('API_KEY')
        
        if not expected_token or token != expected_token:
            return jsonify({"error": "Token inválido"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# Rota de health check
@app.route('/health')
def health_check():
    """Endpoint para verificação de saúde da aplicação"""
    return jsonify({"status": "healthy"}), 200

# Registrar blueprint web
app.register_blueprint(web_bp, url_prefix='/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.PORT, debug=config.DEBUG)