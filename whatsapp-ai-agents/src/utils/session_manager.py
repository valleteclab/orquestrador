import redis
import json
import logging
import requests
from typing import Dict, Any, Optional

class SessionManager:
    """Gerenciador de sessões para armazenar o estado das conversas"""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.logger = logging.getLogger(__name__)

    def create_session(self, phone_number: str, initial_data: Dict[str, Any] = None) -> bool:
        """Cria uma nova sessão para um número de telefone"""
        try:
            session_data = {
                'phone_number': phone_number,
                'created_at': self._get_timestamp(),
                'last_activity': self._get_timestamp(),
                'context': {},
                'conversation_history': [],
                'agent_state': 'idle'
            }

            if initial_data:
                session_data.update(initial_data)

            self.redis_client.set(f"session:{phone_number}", json.dumps(session_data))
            self.logger.info(f"Sessão criada para {phone_number}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao criar sessão para {phone_number}: {e}")
            return False

    def get_session(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Recupera os dados da sessão de um número de telefone"""
        try:
            session_data = self.redis_client.get(f"session:{phone_number}")
            if session_data:
                return json.loads(session_data)
            return None
        except Exception as e:
            self.logger.error(f"Erro ao recuperar sessão para {phone_number}: {e}")
            return None

    def update_session(self, phone_number: str, data: Dict[str, Any]) -> bool:
        """Atualiza os dados da sessão de um número de telefone"""
        try:
            session_data = self.get_session(phone_number)
            if not session_data:
                return self.create_session(phone_number, data)

            session_data.update(data)
            session_data['last_activity'] = self._get_timestamp()

            self.redis_client.set(f"session:{phone_number}", json.dumps(session_data))
            self.logger.info(f"Sessão atualizada para {phone_number}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao atualizar sessão para {phone_number}: {e}")
            return False

    def delete_session(self, phone_number: str) -> bool:
        """Deleta a sessão de um número de telefone"""
        try:
            result = self.redis_client.delete(f"session:{phone_number}")
            if result:
                self.logger.info(f"Sessão deletada para {phone_number}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erro ao deletar sessão para {phone_number}: {e}")
            return False

    def _get_timestamp(self) -> str:
        """Retorna o timestamp atual"""
        from datetime import datetime
        return datetime.now().isoformat()

class ChatwootClient:
    """Cliente para integração com a API do Chatwoot"""

    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        self.logger = logging.getLogger(__name__)

    def send_message(self, inbox_id: int, contact_identifier: str, message: str) -> Optional[Dict[str, Any]]:       
        """Envia uma mensagem através da API do Chatwoot"""
        try:
            url = f"{self.base_url}/api/v1/inboxes/{inbox_id}/contacts"
            payload = {
                "source_id": contact_identifier,
                "body": message
            }

            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            self.logger.info(f"Mensagem enviada para {contact_identifier}")
            return response.json()
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem para {contact_identifier}: {e}")
            return None

    def get_conversation(self, inbox_id: int, contact_identifier: str) -> Optional[Dict[str, Any]]:
        """Obtém a conversa de um contato específico"""
        try:
            url = f"{self.base_url}/api/v1/inboxes/{inbox_id}/contacts/{contact_identifier}/conversations"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            self.logger.error(f"Erro ao obter conversa para {contact_identifier}: {e}")
            return None