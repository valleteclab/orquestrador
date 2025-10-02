from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json
from .base_orchestrator import BaseOrchestrator
from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class AgentOrchestrator(BaseOrchestrator):
    """Implementação concreta do orquestrador de agentes"""
    
    def __init__(self, config: Any = None):
        super().__init__()
        self.config = config or {}
        self.routing_rules: Dict[str, str] = {}
        self.metrics: Dict[str, Any] = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'agent_usage': {}
        }
        
    def register_agent(self, agent_id: str, agent_instance: BaseAgent) -> bool:
        """Registra um novo agente no orquestrador"""
        try:
            if not isinstance(agent_instance, BaseAgent):
                logger.error(f"Agente {agent_id} não é uma instância válida de BaseAgent")
                return False
                
            self.agents[agent_id] = agent_instance
            self.metrics['agent_usage'][agent_id] = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'last_used': None
            }
            logger.info(f"Agente {agent_id} registrado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao registrar agente {agent_id}: {str(e)}")
            return False
    
    def route_request(self, request_data: Dict[str, Any]) -> str:
        """Roteia a solicitação para o agente apropriado"""
        try:
            self.metrics['total_requests'] += 1
            
            # Lógica de roteamento baseada no tipo de mensagem
            message_type = request_data.get('message_type', 'default')
            content = request_data.get('content', '')
            
            # Regras de roteamento simples
            if 'suporte' in content.lower() or 'ajuda' in content.lower():
                target_agent = 'customer_service'
            elif 'financeiro' in content.lower() or 'pagamento' in content.lower():
                target_agent = 'financial'
            elif 'técnico' in content.lower() or 'problema' in content.lower():
                target_agent = 'technical_support'
            else:
                target_agent = 'customer_service'  # Agente padrão
            
            # Verificar se o agente existe
            if target_agent not in self.agents:
                logger.warning(f"Agente {target_agent} não encontrado, usando agente padrão")
                target_agent = 'customer_service'
                
                if target_agent not in self.agents:
                    logger.error("Nenhum agente disponível para processar a solicitação")
                    return None
            
            # Atualizar métricas
            self.metrics['agent_usage'][target_agent]['total_requests'] += 1
            self.metrics['agent_usage'][target_agent]['last_used'] = datetime.now().isoformat()
            
            logger.info(f"Solicitação roteada para o agente: {target_agent}")
            return target_agent
            
        except Exception as e:
            logger.error(f"Erro no roteamento da solicitação: {str(e)}")
            self.metrics['failed_requests'] += 1
            return None
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Retorna o status de um agente específico"""
        if agent_id not in self.agents:
            return {'error': f'Agente {agent_id} não encontrado'}
            
        agent = self.agents[agent_id]
        return {
            'agent_id': agent_id,
            'is_active': hasattr(agent, 'is_active') and agent.is_active,
            'capabilities': getattr(agent, 'capabilities', []),
            'metrics': self.metrics['agent_usage'].get(agent_id, {}),
            'last_heartbeat': getattr(agent, 'last_heartbeat', None)
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna o status geral do sistema"""
        agent_statuses = {}
        for agent_id in self.agents:
            agent_statuses[agent_id] = self.get_agent_status(agent_id)
            
        return {
            'timestamp': datetime.now().isoformat(),
            'total_agents': len(self.agents),
            'active_agents': len([a for a in self.agents.values() if hasattr(a, 'is_active') and a.is_active]),
            'agents': agent_statuses,
            'metrics': self.metrics,
            'system_health': 'healthy' if len(self.agents) > 0 else 'degraded'
        }
    
    def add_routing_rule(self, keyword: str, agent_id: str) -> bool:
        """Adiciona uma regra de roteamento personalizada"""
        try:
            self.routing_rules[keyword.lower()] = agent_id
            logger.info(f"Regra de roteamento adicionada: {keyword} -> {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar regra de roteamento: {str(e)}")
            return False
    
    def remove_routing_rule(self, keyword: str) -> bool:
        """Remove uma regra de roteamento personalizada"""
        try:
            if keyword.lower() in self.routing_rules:
                del self.routing_rules[keyword.lower()]
                logger.info(f"Regra de roteamento removida: {keyword}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao remover regra de roteamento: {str(e)}")
            return False