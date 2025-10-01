def load_from_env(self):
        """Carrega as configurações a partir de variáveis de ambiente"""
        import os
        from dotenv import load_dotenv
        
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