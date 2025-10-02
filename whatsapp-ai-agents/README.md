# Descrição do projeto
Este projeto implementa um sistema de agentes de IA para atendimento integrado com o Chatwoot, que por sua vez está conectado ao WhatsApp. Inclui uma interface web para gerenciamento dos agentes.

## Documentação Completa
Toda a documentação do projeto está disponível na pasta [docs/](docs/):

- [Product Requirements Document (PRD)](docs/PRD.md) - Visão completa do produto
- [Documentação Técnica](docs/technical.md) - Detalhes de arquitetura e implementação
- [Guia de Contribuição](docs/contributing.md) - Como contribuir para o projeto
- [Changelog](docs/CHANGELOG.md) - Histórico de versões
- [Deployment](docs/deployment.md) - Guia completo para implantação em VPS
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Soluções para problemas comuns

## Estrutura do projeto
- `src/`: Código fonte da aplicação
  - `agents/`: Implementação dos agentes de IA
  - `config/`: Arquivos de configuração
  - `orchestrator/`: Sistema de orquestração de agentes
  - `utils/`: Utilitários e classes auxiliares
  - `web/`: Interface web para gerenciamento
- `requirements.txt`: Dependências do projeto

## Arquitetura do Orquestrador de Agentes

O sistema agora utiliza uma arquitetura de orquestração de agentes que permite:

### Componentes Principais

1. **Orquestrador Central** (`src/orchestrator/orchestrator.py`)
   - Gerencia o registro e ciclo de vida dos agentes
   - Implementa lógica de roteamento de solicitações
   - Coleta e fornece métricas de desempenho
   - Monitora o status dos agentes

2. **Agentes Especializados** (`src/orchestrator/specialized_agents.py`)
   - `TechnicalSupportAgent`: Trata problemas técnicos
   - `FinancialAgent`: Lida com questões financeiras
   - `CustomerServiceAgent`: Atendimento geral ao cliente

3. **Gerenciador de Sessões** (`src/orchestrator/session_manager.py`)
   - Mantém o contexto das conversas
   - Armazena estado das interações com usuários
   - Integração com Redis para persistência

4. **Coletor de Métricas** (`src/orchestrator/metrics.py`)
   - Monitora desempenho dos agentes
   - Coleta estatísticas de uso
   - Fornece dados para otimização

### Funcionamento

1. **Recebimento de Mensagens**: Webhook do Chatwoot recebe mensagens
2. **Roteamento Inteligente**: Orquestrador analisa conteúdo e encaminha ao agente adequado
3. **Processamento**: Agente especializado trata a solicitação
4. **Resposta**: Resposta é enviada de volta ao usuário via Chatwoot/WhatsApp

## Endpoints da API

- `POST /webhook` - Recebe mensagens do Chatwoot
- `GET /health` - Verifica saúde da aplicação
- `GET /api/orchestrator/status` - Status do orquestrador (requer API key)
- `GET /api/orchestrator/agent/<agent_id>` - Status de agente específico (requer API key)
- `GET /admin/*` - Interface web de administração

## Instalação e Execução

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd whatsapp-ai-agents

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp src/config/.env.example src/config/.env
# Edite o arquivo .env com suas configurações

# Execute a aplicação
python src/main.py
```