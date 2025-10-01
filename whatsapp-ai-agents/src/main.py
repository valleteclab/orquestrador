from flask import Flask, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from twilio.twiml.messaging_response import MessagingResponse
from src.config.config import Config
from src.utils.session_manager import SessionManager
from src.agents.customer_service_agent import CustomerServiceAgent, TechnicalSupportAgent
from src.web.routes import web_bp
import logging
import traceback
import json
import requests
from functools import wraps

# Modelos de usuário para autenticação (simplificados para este exemplo)
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Função de autenticação básica (em produção, use um sistema de autenticação adequado)
def authenticate_user(username, password):
    # Em produção, verifique as credenciais em um banco de dados
    if username == "admin" and password == "admin":
        return User(1)
    return None

# Decorador para verificar chave de API
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-KEY')
        if api_key != 'sua_chave_secreta_aqui':  # Em produção, use uma chave segura
            return jsonify({"error": "Chave de API inválida"}), 401
        return f(*args, **kwargs)
    return decorated_function

class ChatwootBot:
    """Classe principal para integração com Chatwoot"""
    
    def __init__(self):
        # Carregar configurações
        self.config = Config()
        self.config.load_from_env()
        
        # Inicializar gerenciador de sessões
        self.session_manager = SessionManager(
            host=self.config.REDIS_HOST,
            port=self.config.REDIS_PORT,
            db=self.config.REDIS_DB
        )
        
        # Inicializar cliente Chatwoot
        self.chatwoot_client = None
        if self.config.CHATWOOT_URL and self.config.CHATWOOT_API_TOKEN:
            self.chatwoot_client = self.session_manager.ChatwootClient(
                base_url=self.config.CHATWOOT_URL,
                api_token=self.config.CHATWOOT_API_TOKEN
            )
        
        # Inicializar agentes
        self.customer_service_agent = CustomerServiceAgent()
        self.technical_support_agent = TechnicalSupportAgent()
        
        # Inicializar clientes de API
        self._initialize_apis()
        
        # Configurar logging
        self._setup_logging()
        
    def _initialize_apis(self):
        """Inicializa as APIs necessárias"""
        # Inicializar OpenAI para os agentes
        if self.config.OPENAI_API_KEY:
            self.customer_service_agent.initialize_openai(self.config.OPENAI_API_KEY)
            self.technical_support_agent.initialize_openai(self.config.OPENAI_API_KEY)
        
    def _setup_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            level=logging.INFO if not self.config.DEBUG else logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def _detect_intent(self, message: str) -> str:
        """Detecta a intenção da mensagem para rotear ao agente correto"""
        # Palavras-chave para suporte técnico
        tech_keywords = [
            'erro', 'não funciona', 'problema', 'instalação', 'configuração',
            'bug', 'travando', 'lento', 'conexão', 'rede', 'internet',
            'software', 'aplicativo', 'app', 'sistema', 'atualização'
        ]
        
        # Converter mensagem para minúsculas para comparação
        message_lower = message.lower()
        
        # Verificar se alguma palavra-chave técnica está presente
        for keyword in tech_keywords:
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
            
    def process_message(self, contact_identifier: str, message: str) -> str:
        """Processa uma mensagem recebida do Chatwoot"""
        try:
            # Recuperar ou criar sessão para o contato
            session = self.session_manager.get_session(contact_identifier)
            if not session:
                self.session_manager.create_session(contact_identifier)
                session = self.session_manager.get_session(contact_identifier)
            
            # Detectar intenção da mensagem
            intent = self._detect_intent(message)
            
            # Selecionar agente apropriado
            agent = self._get_agent(intent)
            
            # Processar mensagem com o agente
            response = agent.process_message(message, session)
            
            # Atualizar sessão com o histórico da conversa
            self.session_manager.update_session(contact_identifier, session)
            
            self.logger.info(f"Mensagem processada de {contact_identifier}: {intent}")
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem de {contact_identifier}: {e}")
            self.logger.error(traceback.format_exc())
            return "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."
            
    def send_response(self, contact_identifier: str, message: str) -> bool:
        """Envia uma resposta para o Chatwoot"""
        if not self.chatwoot_client or not self.config.CHATWOOT_INBOX_ID:
            self.logger.error("Chatwoot client não configurado corretamente")
            return False
            
        try:
            result = self.chatwoot_client.send_message(
                inbox_id=self.config.CHATWOOT_INBOX_ID,
                contact_identifier=contact_identifier,
                message=message
            )
            
            return result is not None
        except Exception as e:
            self.logger.error(f"Erro ao enviar resposta para {contact_identifier}: {e}")
            return False

# Criar instância do Flask app
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Em produção, use uma chave segura

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'web.login'

# Usuário para demonstração (em produção, use um banco de dados)
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Inicializar bot
chatwoot_bot = None

# Registrar blueprint da interface web
app.register_blueprint(web_bp, url_prefix='/admin')

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint para receber webhooks do Chatwoot"""
    global chatwoot_bot
    
    try:
        # Inicializar o bot se ainda não estiver inicializado
        if chatwoot_bot is None:
            chatwoot_bot = ChatwootBot()
        
        # Obter dados do webhook
        data = request.get_json()
        
        # Verificar se é uma mensagem de contato
        if data.get('event') == 'message_created' and data.get('message_type') == 'incoming':
            # Extrair informações da mensagem
            contact_identifier = data.get('contact', {}).get('identifier') or data.get('sender', {}).get('identifier')
            message_content = data.get('content')
            
            if contact_identifier and message_content:
                chatwoot_bot.logger.info(f"Mensagem recebida de {contact_identifier}: {message_content}")
                
                # Processar mensagem e obter resposta
                response = chatwoot_bot.process_message(contact_identifier, message_content)
                
                # Enviar resposta de volta ao Chatwoot
                chatwoot_bot.send_response(contact_identifier, response)
        
        # Retornar sucesso
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        logging.error(f"Erro no endpoint do webhook: {e}")
        logging.error(traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """Endpoint para autenticação da API"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = authenticate_user(username, password)
    if user:
        login_user(user)
        return jsonify({"success": True, "message": "Autenticado com sucesso"})
    else:
        return jsonify({"success": False, "message": "Credenciais inválidas"}), 401

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar a saúde da aplicação"""
    return jsonify({"status": "ok", "message": "Chatwoot AI Bot is running"})

if __name__ == '__main__':
    # Inicializar bot e iniciar servidor Flask
    bot_instance = ChatwootBot()
    app.run(debug=bot_instance.config.DEBUG, port=bot_instance.config.PORT, host='0.0.0.0')