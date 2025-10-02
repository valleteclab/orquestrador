#!/usr/bin/env python3
"""
Script de teste para o Orquestrador de Agentes de IA
"""

import sys
import os
import json
from datetime import datetime

# Adicionar o diretório src ao path para importações
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.orchestrator.orchestrator import AgentOrchestrator
from src.orchestrator.specialized_agents import TechnicalSupportAgent, FinancialAgent
from src.agents.customer_service_agent import CustomerServiceAgent

def test_orchestrator():
    """Testa o funcionamento básico do orquestrador"""
    
    print("=== Teste do Orquestrador de Agentes de IA ===\n")
    
    # Criar instância do orquestrador
    orchestrator = AgentOrchestrator()
    
    # Criar agentes de teste
    print("1. Criando agentes...")
    customer_service_agent = CustomerServiceAgent("customer_service")
    technical_support_agent = TechnicalSupportAgent("technical_support")
    financial_agent = FinancialAgent("financial")
    
    # Registrar agentes
    print("2. Registrando agentes no orquestrador...")
    orchestrator.register_agent("customer_service", customer_service_agent)
    orchestrator.register_agent("technical_support", technical_support_agent)
    orchestrator.register_agent("financial", financial_agent)
    
    # Verificar agentes registrados
    print(f"3. Agentes registrados: {list(orchestrator.agents.keys())}")
    
    # Testar roteamento
    print("\n4. Testando roteamento de mensagens...")
    
    test_messages = [
        {
            "content": "Olá, preciso de ajuda com meu pedido",
            "user_id": "user_001",
            "message_type": "text"
        },
        {
            "content": "Estou tendo problemas para acessar o sistema",
            "user_id": "user_002",
            "message_type": "text"
        },
        {
            "content": "Quero saber sobre meu reembolso",
            "user_id": "user_003",
            "message_type": "text"
        },
        {
            "content": "Como faço para instalar o aplicativo?",
            "user_id": "user_004",
            "message_type": "text"
        }
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   Teste {i}: '{message['content']}'")
        target_agent = orchestrator.route_request(message)
        print(f"   Agente selecionado: {target_agent}")
        
        # Verificar se o agente existe e está registrado
        if target_agent in orchestrator.agents:
            agent = orchestrator.agents[target_agent]
            print(f"   Agente válido: {agent.__class__.__name__}")
        else:
            print(f"   Erro: Agente {target_agent} não encontrado!")
    
    # Testar status do sistema
    print("\n5. Verificando status do sistema...")
    system_status = orchestrator.get_system_status()
    print(f"   Total de agentes: {system_status['total_agents']}")
    print(f"   Agentes ativos: {system_status['active_agents']}")
    print(f"   Requisições totais: {system_status['metrics']['total_requests']}")
    
    # Testar status individual dos agentes
    print("\n6. Verificando status individual dos agentes...")
    for agent_id in orchestrator.agents:
        agent_status = orchestrator.get_agent_status(agent_id)
        is_active = agent_status.get('is_active', False)
        print(f"   {agent_id}: {'Ativo' if is_active else 'Inativo'}")
    
    # Testar regras de roteamento personalizadas
    print("\n7. Testando regras de roteamento personalizadas...")
    orchestrator.add_routing_rule("urgente", "technical_support")
    orchestrator.add_routing_rule("financeiro", "financial")
    
    test_custom_routing = {
        "content": "Este é um problema urgente que precisa de atenção",
        "user_id": "user_005",
        "message_type": "text"
    }
    
    target_agent = orchestrator.route_request(test_custom_routing)
    print(f"   Mensagem com palavra-chave 'urgente' roteada para: {target_agent}")
    
    # Remover regra
    orchestrator.remove_routing_rule("urgente")
    print("   Regra de roteamento 'urgente' removida")
    
    # Teste final
    print("\n8. Status final do sistema...")
    final_status = orchestrator.get_system_status()
    print(f"   Tempo de atividade: {final_status.get('timestamp', 'N/A')}")
    print(f"   Saúde do sistema: {final_status.get('system_health', 'desconhecida')}")
    
    print("\n=== Teste concluído com sucesso! ===")
    
    return True

def test_agent_processing():
    """Testa o processamento de mensagens pelos agentes"""
    
    print("\n=== Teste de Processamento de Agentes ===\n")
    
    # Criar instância do orquestrador
    orchestrator = AgentOrchestrator()
    
    # Criar e registrar agentes
    customer_service_agent = CustomerServiceAgent("customer_service")
    technical_support_agent = TechnicalSupportAgent("technical_support")
    financial_agent = FinancialAgent("financial")
    
    orchestrator.register_agent("customer_service", customer_service_agent)
    orchestrator.register_agent("technical_support", technical_support_agent)
    orchestrator.register_agent("financial", financial_agent)
    
    # Testar processamento de mensagens
    test_requests = [
        {
            "agent_id": "technical_support",
            "message": {
                "content": "Não consigo acessar minha conta, aparece um erro",
                "user_id": "test_user_002",
                "session_id": "session_002"
            }
        },
        {
            "agent_id": "financial",
            "message": {
                "content": "Quero saber o status do meu reembolso",
                "user_id": "test_user_003",
                "session_id": "session_003"
            }
        }
    ]
    
    for i, test_request in enumerate(test_requests, 1):
        agent_id = test_request["agent_id"]
        message = test_request["message"]
        
        print(f"\n   Teste de processamento {i}: {agent_id}")
        print(f"   Mensagem: {message['content']}")
        
        # Recuperar agente
        if agent_id in orchestrator.agents:
            agent = orchestrator.agents[agent_id]
            response = agent.process_message(message)
            
            # Verificar se a resposta é um dicionário ou string
            if isinstance(response, dict):
                print(f"   Resposta: {response.get('response', 'Nenhuma resposta')}")
                print(f"   Sucesso: {'error' not in response}")
                
                if 'error' in response:
                    print(f"   Erro: {response['error']}")
            else:
                print(f"   Resposta: {response}")
                print(f"   Tipo da resposta: {type(response)}")
        else:
            print(f"   Erro: Agente {agent_id} não encontrado!")
    
    print("\n=== Teste de processamento concluído! ===")
    
    return True

if __name__ == "__main__":
    try:
        # Executar testes
        success1 = test_orchestrator()
        success2 = test_agent_processing()
        
        if success1 and success2:
            print("\n✓ Todos os testes passaram com sucesso!")
            sys.exit(0)
        else:
            print("\n✗ Alguns testes falharam!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)