from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class BaseOrchestrator(ABC):
    """Classe base abstrata para o orquestrador de agentes"""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.active_sessions: Dict[str, Any] = {}
        
    @abstractmethod
    def register_agent(self, agent_id: str, agent_instance: Any) -> bool:
        """Registra um novo agente no orquestrador"""
        pass
    
    @abstractmethod
    def route_request(self, request_data: Dict[str, Any]) -> str:
        """Roteia a solicitação para o agente apropriado"""
        pass
    
    @abstractmethod
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Retorna o status de um agente específico"""
        pass
    
    @abstractmethod
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna o status geral do sistema"""
        pass