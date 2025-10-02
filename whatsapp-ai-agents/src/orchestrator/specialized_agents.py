from typing import Dict, Any, List
from datetime import datetime
import logging
from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class TechnicalSupportAgent(BaseAgent):
    """Agente especializado em suporte técnico"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any] = None):
        super().__init__(agent_id, "gpt-4")
        self.agent_id = agent_id
        self.config = config
        self.capabilities = ['technical_support', 'troubleshooting', 'system_diagnostics']
        self.is_active = True
        self.last_heartbeat = datetime.now().isoformat()
        
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Processa mensagens de suporte técnico"""
        try:
            self.last_heartbeat = datetime.now().isoformat()
            
            # Extrair informações da mensagem
            content = message.get('content', '')
            user_id = message.get('user_id', 'unknown')
            session_id = message.get('session_id', 'unknown')
            
            logger.info(f"TechnicalSupportAgent processando mensagem de {user_id}: {content}")
            
            # Lógica de processamento específica para suporte técnico
            response = self._analyze_technical_issue(content, message)
            
            return {
                'agent_id': self.agent_id,
                'user_id': user_id,
                'session_id': session_id,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'requires_followup': False
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem no TechnicalSupportAgent: {str(e)}")
            return {
                'agent_id': self.agent_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_technical_issue(self, content: str, message: Dict[str, Any]) -> str:
        """Analisa problemas técnicos específicos"""
        content_lower = content.lower()
        
        # Análise de problemas comuns
        if 'não consigo acessar' in content_lower or 'acesso' in content_lower:
            return "Entendi que você está tendo problemas de acesso. Vamos resolver isso juntos. Primeiro, verifique se sua conexão com a internet está funcionando corretamente."
        
        elif 'lento' in content_lower or 'demora' in content_lower:
            return "Percebi que você está enfrentando lentidão. Isso pode ser causado por vários fatores. Vamos verificar alguns pontos importantes para melhorar o desempenho."
        
        elif 'erro' in content_lower or 'não funciona' in content_lower:
            return "Sinto que você está enfrentando um erro técnico. Para ajudá-lo melhor, preciso de mais detalhes sobre o problema. Pode me descrever exatamente o que acontece?"
        
        elif 'instalação' in content_lower or 'instalar' in content_lower:
            return "Vamos resolver seu problema de instalação. Primeiro, verifique se seu sistema atende aos requisitos mínimos e se você está seguindo os passos corretos."
        
        else:
            return "Entendi que você precisa de ajuda com um problema técnico. Para fornecer a melhor assistência possível, por favor, me descreva detalhadamente o problema que você está enfrentando."
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna o status do agente"""
        return {
            'agent_id': self.agent_id,
            'is_active': self.is_active,
            'capabilities': self.capabilities,
            'last_heartbeat': self.last_heartbeat,
            'type': 'technical_support'
        }

class FinancialAgent(BaseAgent):
    """Agente especializado em questões financeiras"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any] = None):
        super().__init__(agent_id, "gpt-3.5-turbo")
        self.agent_id = agent_id
        self.config = config
        self.capabilities = ['financial', 'payments', 'billing', 'invoices']
        self.is_active = True
        self.last_heartbeat = datetime.now().isoformat()
        
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Processa mensagens financeiras"""
        try:
            self.last_heartbeat = datetime.now().isoformat()
            
            # Extrair informações da mensagem
            content = message.get('content', '')
            user_id = message.get('user_id', 'unknown')
            session_id = message.get('session_id', 'unknown')
            
            logger.info(f"FinancialAgent processando mensagem de {user_id}: {content}")
            
            # Lógica de processamento específica para questões financeiras
            response = self._analyze_financial_issue(content, message)
            
            return {
                'agent_id': self.agent_id,
                'user_id': user_id,
                'session_id': session_id,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'requires_followup': False
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem no FinancialAgent: {str(e)}")
            return {
                'agent_id': self.agent_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _analyze_financial_issue(self, content: str, message: Dict[str, Any]) -> str:
        """Analisa questões financeiras específicas"""
        content_lower = content.lower()
        
        # Análise de problemas financeiros comuns
        if 'pagamento' in content_lower or 'paguei' in content_lower:
            return "Entendi que você tem uma dúvida sobre pagamento. Para verificar o status do seu pagamento, preciso do número da transação ou ID do pedido."
        
        elif 'fatura' in content_lower or 'boleto' in content_lower:
            return "Sobre sua fatura, posso ajudá-lo a verificar valores, datas de vencimento ou segunda via. Por favor, me informe o número da fatura ou o período de referência."
        
        elif 'reembolso' in content_lower or 'devolução' in content_lower:
            return "Sobre reembolsos, nosso processo geralmente leva de 5 a 10 dias úteis após a aprovação. Posso verificar o status do seu reembolso específico se você me fornecer o número do pedido."
        
        elif 'desconto' in content_lower or 'promoção' in content_lower:
            return "Temos várias opções de descontos e promoções disponíveis. Posso verificar quais estão ativas para o seu perfil e ajudá-lo a aproveitá-las."
        
        else:
            return "Entendi que você precisa de ajuda com uma questão financeira. Para fornecer a assistência mais precisa, por favor, detalhe sua dúvida sobre pagamentos, faturas, reembolsos ou qualquer outro assunto financeiro."
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna o status do agente"""
        return {
            'agent_id': self.agent_id,
            'is_active': self.is_active,
            'capabilities': self.capabilities,
            'last_heartbeat': self.last_heartbeat,
            'type': 'financial'
        }