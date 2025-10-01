import openai
import logging
from typing import List, Dict, Any

class BaseAgent:
    """Classe base para agentes de IA"""
    
    def __init__(self, name: str, model: str = "gpt-3.5-turbo"):
        self.name = name
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.openai_client = None
        
    def initialize_openai(self, api_key: str):
        """Inicializa o cliente OpenAI"""
        openai.api_key = api_key
        self.openai_client = openai
        
    def generate_response(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Gera uma resposta usando a API OpenAI"""
        try:
            response = self.openai_client.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Erro ao gerar resposta para agente {self.name}: {e}")
            return "Desculpe, ocorreu um erro ao processar sua solicitação."
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Processa uma mensagem recebida e retorna uma resposta"""
        # Este método deve ser implementado pelas subclasses
        raise NotImplementedError("Método process_message deve ser implementado pela subclasse")