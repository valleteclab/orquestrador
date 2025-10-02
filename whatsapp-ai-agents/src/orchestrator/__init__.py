"""
Inicialização do Orquestrador de Agentes de IA
"""

from src.config.config import Config
from src.orchestrator.orchestrator import AgentOrchestrator
from src.orchestrator.specialized_agents import TechnicalSupportAgent, FinancialAgent
from src.agents.customer_service_agent import CustomerServiceAgent
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_orchestrator():
    """Inicializa o orquestrador com todos os agentes"""
    
    # Carregar configurações
    config = Config()
    config.load_from_env()
    
    # Criar instância do orquestrador
    orchestrator = AgentOrchestrator(config)
    
    # Inicializar agentes
    customer_service_agent = CustomerServiceAgent("customer_service")
    customer_service_agent.initialize_openai(config.OPENAI_API_KEY)
    
    technical_support_agent = TechnicalSupportAgent("technical_support")
    technical_support_agent.initialize_openai(config.OPENAI_API_KEY)
    
    financial_agent = FinancialAgent("financial")
    financial_agent.initialize_openai(config.OPENAI_API_KEY)
    
    # Registrar agentes no orquestrador
    orchestrator.register_agent("customer_service", customer_service_agent)
    orchestrator.register_agent("technical_support", technical_support_agent)
    orchestrator.register_agent("financial", financial_agent)
    
    logger.info("Orquestrador inicializado com sucesso")
    logger.info(f"Agentes registrados: {list(orchestrator.agents.keys())}")
    
    return orchestrator, config

if __name__ == "__main__":
    # Teste de inicialização
    orchestrator, config = initialize_orchestrator()
    
    # Exibir status do sistema
    status = orchestrator.get_system_status()
    print("Status do Orquestrador:")
    print(f"Total de agentes: {status['total_agents']}")
    print(f"Agentes ativos: {status['active_agents']}")
    print("Detalhes dos agentes:")
    for agent_id, agent_status in status['agents'].items():
        print(f"  - {agent_id}: {'Ativo' if agent_status.get('is_active', False) else 'Inativo'}")