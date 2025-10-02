from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import logging
import redis
from src.config.config import Config

logger = logging.getLogger(__name__)

class SessionManager:
    """Gerenciador de sessões para o orquestrador de agentes"""
    
    def __init__(self, config: Config):
        self.config = config
        self.redis_client = None
        self.session_timeout = 3600  # 1 hora
        
        # Conectar ao Redis
        try:
            self.redis_client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                decode_responses=True
            )
            # Testar conexão
            self.redis_client.ping()
            logger.info("Conexão com Redis estabelecida com sucesso")
        except Exception as e:
            logger.error(f"Erro ao conectar ao Redis: {str(e)}")
            self.redis_client = None
    
    def create_session(self, session_id: str, user_id: str, initial_data: Dict[str, Any] = None) -> bool:
        """Cria uma nova sessão"""
        try:
            session_data = {
                'session_id': session_id,
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat(),
                'data': initial_data or {},
                'active_agent': None
            }
            
            if self.redis_client:
                key = f"session:{session_id}"
                self.redis_client.setex(
                    key, 
                    self.session_timeout, 
                    json.dumps(session_data)
                )
                logger.info(f"Sessão criada: {session_id}")
                return True
            else:
                logger.warning("Redis não disponível, sessão não persistida")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao criar sessão {session_id}: {str(e)}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Recupera os dados de uma sessão"""
        try:
            if self.redis_client:
                key = f"session:{session_id}"
                session_data = self.redis_client.get(key)
                if session_data:
                    # Atualizar TTL da sessão
                    self.redis_client.expire(key, self.session_timeout)
                    return json.loads(session_data)
            return None
        except Exception as e:
            logger.error(f"Erro ao recuperar sessão {session_id}: {str(e)}")
            return None
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Atualiza os dados de uma sessão"""
        try:
            if self.redis_client:
                key = f"session:{session_id}"
                session_data = self.get_session(session_id)
                if session_data:
                    # Atualizar dados
                    session_data['last_activity'] = datetime.now().isoformat()
                    session_data['data'].update(data)
                    
                    # Salvar atualização
                    self.redis_client.setex(
                        key, 
                        self.session_timeout, 
                        json.dumps(session_data)
                    )
                    return True
            return False
        except Exception as e:
            logger.error(f"Erro ao atualizar sessão {session_id}: {str(e)}")
            return False
    
    def set_active_agent(self, session_id: str, agent_id: str) -> bool:
        """Define o agente ativo para uma sessão"""
        try:
            session_data = self.get_session(session_id)
            if session_data:
                session_data['active_agent'] = agent_id
                session_data['last_activity'] = datetime.now().isoformat()
                
                if self.redis_client:
                    key = f"session:{session_id}"
                    self.redis_client.setex(
                        key, 
                        self.session_timeout, 
                        json.dumps(session_data)
                    )
                    return True
            return False
        except Exception as e:
            logger.error(f"Erro ao definir agente ativo para sessão {session_id}: {str(e)}")
            return False
    
    def get_active_agent(self, session_id: str) -> Optional[str]:
        """Recupera o agente ativo para uma sessão"""
        try:
            session_data = self.get_session(session_id)
            if session_data:
                return session_data.get('active_agent')
            return None
        except Exception as e:
            logger.error(f"Erro ao recuperar agente ativo para sessão {session_id}: {str(e)}")
            return None
    
    def is_session_active(self, session_id: str) -> bool:
        """Verifica se uma sessão está ativa"""
        try:
            if self.redis_client:
                key = f"session:{session_id}"
                return self.redis_client.exists(key) > 0
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar status da sessão {session_id}: {str(e)}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """Remove sessões expiradas (não necessário com Redis expirando automaticamente)"""
        return 0