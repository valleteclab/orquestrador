import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    # Configurações da API OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Configurações do Chatwoot
    CHATWOOT_API_KEY = os.getenv('CHATWOOT_API_KEY')
    CHATWOOT_ACCOUNT_ID = os.getenv('CHATWOOT_ACCOUNT_ID')
    CHATWOOT_BASE_URL = os.getenv('CHATWOOT_BASE_URL')
    
    # Configurações do Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    # Configurações de Autenticação do Painel
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Chave secreta para autenticação da API
    API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'chave_secreta_padrao')
    
    # Verificar se as variáveis críticas estão definidas
    @classmethod
    def validate(cls):
        """Valida se todas as variáveis de ambiente necessárias estão definidas"""
        required_vars = {
            'OPENAI_API_KEY': cls.OPENAI_API_KEY,
            'CHATWOOT_API_KEY': cls.CHATWOOT_API_KEY,
            'CHATWOOT_ACCOUNT_ID': cls.CHATWOOT_ACCOUNT_ID,
            'CHATWOOT_BASE_URL': cls.CHATWOOT_BASE_URL
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"Variáveis de ambiente não definidas: {', '.join(missing_vars)}")
        
        return True