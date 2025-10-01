import os
from dotenv import load_dotenv

class Config:
    """Classe para gerenciar as configurações da aplicação"""
    
    def __init__(self):
        # Configurações do Twilio (não utilizadas neste projeto, mantidas para compatibilidade)
        self.TWILIO_ACCOUNT_SID = None
        self.TWILIO_AUTH_TOKEN = None
        self.TWILIO_WHATSAPP_NUMBER = None
        
        # Configurações da OpenAI
        self.OPENAI_API_KEY = None
        
        # Configurações do Redis
        self.REDIS_HOST = 'localhost'
        self.REDIS_PORT = 6379
        self.REDIS_DB = 0
        
        # Configurações do Chatwoot
        self.CHATWOOT_URL = None
        self.CHATWOOT_API_TOKEN = None
        self.CHATWOOT_INBOX_ID = None
        
        # Configurações da aplicação
        self.DEBUG = True
        self.PORT = 5000

    def load_from_env(self):
        """Carrega as configurações a partir de variáveis de ambiente"""
        # Carrega as variáveis de ambiente do arquivo .env
        load_dotenv()
        
        # Configurações da OpenAI
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        
        # Configurações do Redis
        self.REDIS_HOST = os.getenv('REDIS_HOST', self.REDIS_HOST)
        self.REDIS_PORT = int(os.getenv('REDIS_PORT', self.REDIS_PORT))
        self.REDIS_DB = int(os.getenv('REDIS_DB', self.REDIS_DB))
        
        # Configurações do Chatwoot
        self.CHATWOOT_URL = os.getenv('CHATWOOT_URL')
        self.CHATWOOT_API_TOKEN = os.getenv('CHATWOOT_API_TOKEN')
        self.CHATWOOT_INBOX_ID = os.getenv('CHATWOOT_INBOX_ID')
        
        # Configurações da aplicação
        self.DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
        self.PORT = int(os.getenv('PORT', self.PORT))