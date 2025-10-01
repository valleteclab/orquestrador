# Documentação Técnica
## Arquitetura e Componentes do Sistema

### Estrutura de Diretórios

```
whatsapp-ai-agents/
├── docs/                    # Documentação do projeto
├── src/                     # Código fonte principal
│   ├── agents/             # Implementação dos agentes de IA
│   ├── config/             # Arquivos de configuração
│   ├── utils/              # Utilitários e classes auxiliares
│   ├── web/                # Interface web e rotas
│   └── main.py             # Arquivo principal da aplicação
├── requirements.txt        # Dependências do projeto
├── README.md               # Instruções de uso
└── .env.example            # Exemplo de variáveis de ambiente
```

### Componentes Principais

#### 1. Agentes de IA (`src/agents/`)
- `base_agent.py`: Classe base para todos os agentes
- `customer_service_agent.py`: Agentes especializados em atendimento e suporte técnico

#### 2. Configuração (`src/config/`)
- `config.py`: Gerenciamento de configurações do sistema
- `.env.example`: Exemplo de variáveis de ambiente

#### 3. Utilitários (`src/utils/`)
- `session_manager.py`: Gerenciamento de sessões com Redis e cliente Chatwoot

#### 4. Interface Web (`src/web/`)
- `routes.py`: Rotas da interface administrativa
- `templates/`: Templates HTML
- `static/`: Arquivos estáticos (CSS, JS)

#### 5. Arquivo Principal (`src/main.py`)
- Integração com Chatwoot
- Servidor Flask e API
- Autenticação e segurança

## API Endpoints

### Webhooks
- `POST /webhook`: Recebe mensagens do Chatwoot

### Interface Administrativa
- `GET /admin/`: Dashboard principal
- `GET /admin/agents`: Gerenciamento de agentes
- `GET /admin/logs`: Visualização de logs
- `GET /admin/settings`: Configurações do sistema

### API Interna
- `POST /api/auth/login`: Autenticação
- `GET /api/logs`: Logs em tempo real
- `POST /api/test-agent`: Teste de agentes
- `POST /api/agent-config`: Configuração de agentes
- `GET /api/stats`: Estatísticas do sistema
- `GET /health`: Health check

## Fluxo de Processamento

1. **Recepção de Mensagem**
   - Chatwoot envia webhook para `/webhook`
   - Sistema extrai conteúdo e identificador do contato
   - Sessão é recuperada ou criada no Redis

2. **Processamento**
   - Intenção da mensagem é detectada
   - Mensagem é roteada para o agente apropriado
   - Agente processa mensagem com histórico da conversa
   - Resposta é gerada usando API da OpenAI

3. **Resposta**
   - Resposta é enviada ao Chatwoot via API
   - Sessão é atualizada com novo histórico
   - Métricas são atualizadas

## Configurações Necessárias

### Variáveis de Ambiente
- `OPENAI_API_KEY`: Chave de API da OpenAI
- `CHATWOOT_URL`: URL da instância Chatwoot
- `CHATWOOT_API_TOKEN`: Token de API do Chatwoot
- `CHATWOOT_INBOX_ID`: ID da inbox do WhatsApp
- `REDIS_HOST`: Host do servidor Redis
- `REDIS_PORT`: Porta do servidor Redis
- `REDIS_DB`: Banco de dados Redis

### Configurações dos Agentes
- Modelo GPT (gpt-3.5-turbo ou gpt-4)
- Temperatura (0.0-1.0)
- Máximo de tokens por resposta
- Prompt system específico por agente